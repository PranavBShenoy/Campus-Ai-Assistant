from pydantic import BaseModel
from typing import Annotated, Optional, List, Literal
from pydantic import Field, field_validator, model_validator
from datetime import date, datetime

class Subject(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    topics: List[str] = Field(default_factory=lambda: ["General study"])
    exam_date: date
    exam_type: Optional[Literal[
        'mcq', 'final_exam', 'mid_sem', 'unit_test',
        'internal_assessment', 'practical', 'general_study'
    ]] = 'general_study'
    # Defaults retain compatibility with older saved plans without asking users
    # for non-essential planning inputs.
    difficulty: Literal['easy', 'medium', 'hard'] = 'medium'
    priority: Literal['low', 'medium', 'high'] = 'medium'
    current_level: Literal['beginner', 'intermediate', 'advanced'] = 'intermediate'

    @field_validator("topics", mode="before")
    @classmethod
    def default_topics(cls, value):
        return value or ["General study"]

class StudySession(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    date: date
    subject: str
    topic: str
    duration_minutes: int = Field(gt=0, le=1440)
    session_type: Literal['study', 'revision', 'practice', 'mock_test']
    is_completed: bool = False
    notes: Optional[str] = Field(default=None, max_length=5000)

    @field_validator("session_type", mode="before")
    @classmethod
    def normalize_session_type(cls, value):
        normalized = str(value or "study").strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "final_revision": "revision", "review": "revision", "final_review": "revision",
            "quiz": "practice", "questions": "practice", "test": "mock_test",
            "mock": "mock_test", "break": "revision",
        }
        normalized = aliases.get(normalized, normalized)
        return normalized if normalized in {"study", "revision", "practice", "mock_test"} else "study"

class StudyPlanConstraints(BaseModel):
    daily_hours: float = Field(gt=0, le=24)
    preferred_time: Literal['morning', 'afternoon', 'evening', 'flexible']
    break_frequency_minutes: int = 90
    weekly_off_days: List[Annotated[int, Field(ge=0, le=6)]] = Field(default_factory=list)
    start_date: date = Field(default_factory=date.today)

    @field_validator("weekly_off_days")
    @classmethod
    def unique_off_days(cls, value: List[int]) -> List[int]:
        if len(value) != len(set(value)):
            raise ValueError("weekly_off_days must not contain duplicates")
        if len(value) == 7:
            raise ValueError("weekly_off_days must leave at least one study day")
        return value

class GeneratePlanRequest(BaseModel):
    title: str = Field(default="Study Plan", min_length=1, max_length=200)
    subjects: List[Subject] = Field(min_length=1)
    constraints: StudyPlanConstraints
    session_id: Optional[str] = None

    @model_validator(mode="after")
    def exams_follow_start_date(self):
        invalid = [subject.name for subject in self.subjects if subject.exam_date < self.constraints.start_date]
        if invalid:
            raise ValueError("Exam dates must be on or after the plan start date: " + ", ".join(invalid))
        return self

class StudyPlanResponse(BaseModel):
    model_config = {'from_attributes': True, 'use_enum_values': True}
    id: str
    title: str
    subjects: List[Subject]
    sessions: List[StudySession]
    constraints: StudyPlanConstraints
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime
    is_active: bool
    total_sessions: int
    completed_sessions: int

class ModifyPlanRequest(BaseModel):
    plan_id: str
    instruction: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = None

class ModifyPlanInstruction(BaseModel):
    instruction: str = Field(min_length=1, max_length=2000)

class UpdateSessionRequest(BaseModel):
    session_id: Optional[str] = None
    is_completed: Optional[bool] = None
    notes: Optional[str] = Field(default=None, max_length=5000)
    date: Optional[date] = None
    duration_minutes: Optional[int] = Field(default=None, gt=0, le=1440)


