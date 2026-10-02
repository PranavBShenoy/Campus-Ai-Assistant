from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import StudyPlan
from app.schemas.study_plan import GeneratePlanRequest, StudyPlanResponse, ModifyPlanRequest, UpdateSessionRequest, StudySession
from app.graph.study_plan_workflow import generate_study_plan, modify_study_plan
import uuid, logging
from collections import defaultdict
from datetime import date, datetime, timedelta

logger = logging.getLogger('campus_ai.api')

class StudyPlanService:
    async def generate_plan(self, request: GeneratePlanRequest, user_id: str, db: AsyncSession) -> StudyPlanResponse:
        today = date.today().isoformat()

        # Prefer the configured OpenRouter planner, but never leave the UI stuck
        # when a model returns prose, a bad enum (for example final_revision),
        # or an otherwise invalid schedule.
        try:
            plan_data = await generate_study_plan(
                subjects=[s.model_dump(mode="json") for s in request.subjects],
                constraints=request.constraints.model_dump(mode="json"),
                today=today,
            )
            sessions = self._normalise_generated_sessions(plan_data, request.subjects)
            if not sessions:
                raise ValueError("empty schedule")
            sessions = self._schedule_sessions(sessions, request.subjects, request.constraints)
            self._validate_schedule(sessions, request.subjects, request.constraints)
        except Exception:
            logger.warning("AI plan was unusable; using deterministic planner", exc_info=True)
            sessions = self._build_fallback_sessions(request.subjects, request.constraints)
            self._validate_schedule(sessions, request.subjects, request.constraints)

        start_date = request.constraints.start_date
        end_date = max((session.date for session in sessions), default=start_date)
        
        plan = StudyPlan(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            user_id=user_id,
            title=request.title,
            subjects_json=[s.model_dump(mode="json") for s in request.subjects],
            constraints_json=request.constraints.model_dump(mode="json"),
            sessions_json=[s.model_dump(mode="json") for s in sessions],
            start_date=start_date,
            end_date=end_date,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        
        return self._to_response(plan)
        
    async def get_plans(self, user_id: str, db: AsyncSession) -> list[StudyPlanResponse]:
        result = await db.execute(
            select(StudyPlan)
            .where(StudyPlan.user_id == user_id, StudyPlan.is_active == True)
            .order_by(StudyPlan.created_at.desc())
        )
        plans = result.scalars().all()
        return [self._to_response(p) for p in plans]
        
    async def get_plan(self, plan_id: str, user_id: str, db: AsyncSession) -> Optional[StudyPlanResponse]:
        result = await db.execute(select(StudyPlan).where(StudyPlan.id == plan_id, StudyPlan.user_id == user_id))
        plan = result.scalar_one_or_none()
        if not plan:
            return None
        return self._to_response(plan)
        
    async def update_plan(self, plan_id: str, user_id: str, updates: dict, db: AsyncSession) -> Optional[StudyPlanResponse]:
        result = await db.execute(select(StudyPlan).where(StudyPlan.id == plan_id, StudyPlan.user_id == user_id))
        plan = result.scalar_one_or_none()
        if not plan:
            return None
            
        if "title" in updates:
            plan.title = updates["title"]
        if "is_active" in updates:
            plan.is_active = updates["is_active"]
            
        plan.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(plan)
        return self._to_response(plan)
        
    async def modify_plan(self, request: ModifyPlanRequest, user_id: str, db: AsyncSession) -> Optional[StudyPlanResponse]:
        result = await db.execute(
            select(StudyPlan).where(
                StudyPlan.id == request.plan_id,
                StudyPlan.user_id == user_id,
            )
        )
        plan = result.scalar_one_or_none()
        if not plan:
            return None
            
        plan_data_for_workflow = {
            "start_date": self._as_date(plan.start_date).isoformat(),
            "end_date": self._as_date(plan.end_date).isoformat(),
            "subjects": plan.subjects_json,
            "constraints": plan.constraints_json,
            "sessions": plan.sessions_json
        }
        
        today = date.today().isoformat()
        new_plan_data = await modify_study_plan(
            existing_plan=plan_data_for_workflow,
            instruction=request.instruction,
            today=today
        )
        
        old_completed = {s["id"]: s for s in plan.sessions_json if s.get("is_completed", False)}
        
        new_sessions = []
        for session_data in new_plan_data.get("sessions", []):
            session = StudySession(**session_data)
            normalized = session.model_dump(mode="json")
            if session.id in old_completed:
                normalized["is_completed"] = True
                normalized["notes"] = old_completed[session.id].get("notes")
            new_sessions.append(normalized)

        if not new_sessions:
            raise ValueError("The model returned a modified plan with no sessions.")

        validated_sessions = self._schedule_sessions(
            [StudySession(**s) for s in new_sessions],
            plan.subjects_json,
            plan.constraints_json,
        )
        self._validate_schedule(validated_sessions, plan.subjects_json, plan.constraints_json)
        new_sessions = [s.model_dump(mode="json") for s in validated_sessions]
                
        plan.sessions_json = new_sessions
        plan.end_date = max(datetime.fromisoformat(s["date"]).date() for s in new_sessions)
        plan.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(plan)
        
        return self._to_response(plan)
        
    async def update_session(self, plan_id: str, user_id: str, request: UpdateSessionRequest, db: AsyncSession) -> Optional[StudyPlanResponse]:
        result = await db.execute(select(StudyPlan).where(StudyPlan.id == plan_id, StudyPlan.user_id == user_id))
        plan = result.scalar_one_or_none()
        if not plan:
            return None
            
        updated = False
        new_sessions = []
        for existing in plan.sessions_json:
            s = dict(existing)
            if s["id"] == request.session_id:
                if request.is_completed is not None:
                    s["is_completed"] = request.is_completed
                if request.notes is not None:
                    s["notes"] = request.notes
                if request.date is not None:
                    s["date"] = request.date.isoformat()
                if request.duration_minutes is not None:
                    s["duration_minutes"] = request.duration_minutes
                updated = True
            new_sessions.append(s)
            
        if updated:
            self._validate_schedule(
                [StudySession(**s) for s in new_sessions],
                plan.subjects_json,
                plan.constraints_json,
            )
            plan.sessions_json = new_sessions
            plan.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(plan)
            
        return self._to_response(plan) if updated else None
        
    def _to_response(self, plan: StudyPlan) -> StudyPlanResponse:
        sessions = [StudySession(**s) for s in plan.sessions_json] if plan.sessions_json else []
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.is_completed])
        
        constraints = dict(plan.constraints_json or {})
        if "daily_hours" not in constraints and "daily_study_hours" in constraints:
            constraints["daily_hours"] = constraints.pop("daily_study_hours")
        constraints.setdefault("start_date", self._as_date(plan.start_date).isoformat())
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        constraints["weekly_off_days"] = [
            day_names.index(day.lower()) if isinstance(day, str) and day.lower() in day_names else day
            for day in constraints.get("weekly_off_days", [])
        ]

        return StudyPlanResponse(
            id=plan.id,
            session_id=plan.session_id,
            title=plan.title,
            start_date=self._as_date(plan.start_date),
            end_date=self._as_date(plan.end_date),
            is_active=plan.is_active,
            subjects=plan.subjects_json,
            constraints=constraints,
            sessions=sessions,
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            created_at=plan.created_at,
            updated_at=plan.updated_at
        )

    @staticmethod
    def _as_date(value) -> date:
        return value.date() if isinstance(value, datetime) else value

    def _validate_schedule(self, sessions, subjects, constraints) -> None:
        start_date = self._as_date(constraints.start_date) if hasattr(constraints, "start_date") else date.fromisoformat(str(constraints["start_date"]))
        daily_hours = float(constraints.daily_hours) if hasattr(constraints, "daily_hours") else float(constraints.get("daily_hours", constraints.get("daily_study_hours", 0)))
        raw_off_days = constraints.weekly_off_days if hasattr(constraints, "weekly_off_days") else constraints.get("weekly_off_days", [])
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        off_days = {
            day_names.index(day.lower()) if isinstance(day, str) and day.lower() in day_names else int(day)
            for day in raw_off_days
        }
        subject_items = subjects if isinstance(subjects, list) else list(subjects)
        subject_deadlines = {
            (item.name if hasattr(item, "name") else item["name"]):
            self._as_date(item.exam_date) if hasattr(item, "exam_date") else date.fromisoformat(str(item["exam_date"]))
            for item in subject_items
        }
        minutes_by_day = defaultdict(int)
        seen_ids = set()
        errors = []

        for session in sessions:
            if session.id in seen_ids:
                errors.append(f"Duplicate session id: {session.id}")
            seen_ids.add(session.id)
            if session.date < start_date:
                errors.append(f"Session {session.id} is before the plan start date.")
            if session.date.weekday() in off_days:
                errors.append(f"Session {session.id} is scheduled on a weekly off day.")
            deadline = subject_deadlines.get(session.subject)
            if deadline is None:
                errors.append(f"Session {session.id} references an unknown subject.")
            elif session.date > deadline:
                errors.append(f"Session {session.id} is after the {session.subject} exam date.")
            minutes_by_day[session.date] += session.duration_minutes

        daily_limit = round(daily_hours * 60)
        for session_date, total_minutes in minutes_by_day.items():
            if total_minutes > daily_limit:
                errors.append(
                    f"Sessions on {session_date.isoformat()} exceed the daily-hours limit."
                )

        if errors:
            raise ValueError("Invalid study plan: " + " ".join(errors[:5]))

    def _schedule_sessions(self, sessions, subjects, constraints) -> list[StudySession]:
        """Deterministically move generated sessions onto valid study days."""
        start_date = self._as_date(constraints.start_date) if hasattr(constraints, "start_date") else date.fromisoformat(str(constraints["start_date"]))
        daily_hours = float(constraints.daily_hours) if hasattr(constraints, "daily_hours") else float(constraints.get("daily_hours", constraints.get("daily_study_hours", 0)))
        raw_off_days = constraints.weekly_off_days if hasattr(constraints, "weekly_off_days") else constraints.get("weekly_off_days", [])
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        off_days = {
            day_names.index(day.lower()) if isinstance(day, str) and day.lower() in day_names else int(day)
            for day in raw_off_days
        }
        if len(off_days) == 7:
            raise ValueError("Invalid study plan: at least one weekly study day is required.")

        subject_items = subjects if isinstance(subjects, list) else list(subjects)
        deadlines = {
            (item.name if hasattr(item, "name") else item["name"]):
            self._as_date(item.exam_date) if hasattr(item, "exam_date") else date.fromisoformat(str(item["exam_date"]))
            for item in subject_items
        }
        latest_deadline = max(deadlines.values())
        daily_limit = round(daily_hours * 60)
        minutes_by_day = defaultdict(int)
        scheduled = []

        for session in sessions:
            deadline = deadlines.get(session.subject, latest_deadline)
            desired = max(session.date, start_date)

            def fits(candidate: date) -> bool:
                if candidate.weekday() in off_days or candidate > deadline:
                    return False
                return minutes_by_day[candidate] + session.duration_minutes <= daily_limit

            candidate = desired
            while candidate <= deadline and not fits(candidate):
                candidate += timedelta(days=1)

            # If the model placed a session too late, use the first earlier slot.
            if candidate > deadline:
                candidate = start_date
                while candidate < desired and not fits(candidate):
                    candidate += timedelta(days=1)

            if not fits(candidate):
                raise ValueError(
                    f"Invalid study plan: no available slot for session {session.id} "
                    f"before the {session.subject} exam date."
                )

            updated = session.model_copy(update={"date": candidate})
            scheduled.append(updated)
            minutes_by_day[candidate] += updated.duration_minutes

        return scheduled

    def _normalise_generated_sessions(self, plan_data, subjects) -> list[StudySession]:
        """Salvage common model formatting mistakes without inventing content."""
        subject_names = {s.name for s in subjects}
        sessions: list[StudySession] = []
        for index, raw in enumerate((plan_data or {}).get("sessions", [])):
            if not isinstance(raw, dict) or raw.get("subject") not in subject_names:
                continue
            item = dict(raw)
            item.setdefault("id", f"session-{index + 1}-{uuid.uuid4().hex[:8]}")
            item.setdefault("topic", "General study")
            item.setdefault("duration_minutes", 60)
            item.setdefault("session_type", "study")
            item.setdefault("is_completed", False)
            try:
                item["duration_minutes"] = max(1, min(1440, int(float(item["duration_minutes"]))))
                sessions.append(StudySession(**item))
            except Exception:
                continue
        return sessions

    def _build_fallback_sessions(self, subjects, constraints) -> list[StudySession]:
        """Create a bounded, valid plan when model output cannot be repaired."""
        start = constraints.start_date
        daily_limit = max(1, round(float(constraints.daily_hours) * 60))
        duration = min(60, daily_limit)
        off_days = set(constraints.weekly_off_days)
        minutes_by_day = defaultdict(int)
        sessions: list[StudySession] = []

        def reserve(deadline: date) -> date | None:
            candidate = start
            while candidate <= deadline:
                if candidate.weekday() not in off_days and minutes_by_day[candidate] + duration <= daily_limit:
                    minutes_by_day[candidate] += duration
                    return candidate
                candidate += timedelta(days=1)
            return None

        for subject in sorted(subjects, key=lambda item: item.exam_date):
            topics = ", ".join(subject.topics) or "General study"
            tasks = [("study", topics), ("revision", topics), ("practice", topics)]
            if subject.exam_type and subject.exam_type != "general_study":
                tasks.append(("mock_test", f"{subject.exam_type.replace('_', ' ').title()} practice"))
            created = 0
            for session_type, topic in tasks:
                slot = reserve(subject.exam_date)
                if slot is None:
                    if created == 0:
                        raise ValueError(
                            f"No study time is available for {subject.name} before its exam. "
                            "Change the exam date, daily hours, or off days."
                        )
                    break
                sessions.append(StudySession(
                    id=f"{uuid.uuid4()}", date=slot, subject=subject.name,
                    topic=topic[:500], duration_minutes=duration,
                    session_type=session_type, is_completed=False,
                ))
                created += 1
        return sessions

