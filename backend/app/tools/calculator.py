from langchain.tools import tool
from datetime import datetime
import math

@tool
def calculate_study_hours(available_days: int, hours_per_day: float) -> dict:
    """Calculate the total study hours available given days and hours per day."""
    total_hours = available_days * hours_per_day
    return {
        "total_hours": total_hours,
        "description": f"Total of {total_hours} hours over {available_days} days."
    }

@tool
def allocate_subject_hours(total_hours: float, subjects: list[dict]) -> dict:
    """Allocate total study hours across subjects based on difficulty, priority, and current level."""
    # Weights for difficulty
    diff_weight = {"easy": 1, "medium": 2, "hard": 3}
    # Weights for priority
    prio_weight = {"low": 1, "medium": 2, "high": 3}
    # Inverse weights for level (lower level needs more time)
    level_weight = {"beginner": 3, "intermediate": 2, "advanced": 1}
    
    total_weight = 0
    subject_weights = {}
    
    for subj in subjects:
        w = (
            diff_weight.get(subj.get("difficulty", "medium"), 2) *
            prio_weight.get(subj.get("priority", "medium"), 2) *
            level_weight.get(subj.get("current_level", "intermediate"), 2)
        )
        subject_weights[subj["name"]] = w
        total_weight += w
        
    allocated = {}
    if total_weight == 0:
        return allocated
        
    for name, w in subject_weights.items():
        allocated[name] = round((w / total_weight) * total_hours, 2)
        
    return allocated

@tool
def calculate_sessions(subject_hours: dict[str, float], session_duration_minutes: int) -> dict:
    """Calculate the number of sessions needed for each subject given a session duration."""
    sessions = {}
    duration_hours = session_duration_minutes / 60.0
    if duration_hours <= 0:
        return sessions
        
    for name, hours in subject_hours.items():
        sessions[name] = math.ceil(hours / duration_hours)
        
    return sessions

@tool
def days_until_exam(exam_date: str, today: str) -> dict:
    """Calculate days and weeks until an exam date."""
    try:
        exam_dt = datetime.fromisoformat(exam_date)
        today_dt = datetime.fromisoformat(today)
        delta = (exam_dt - today_dt).days
        return {
            "days": delta,
            "weeks": round(delta / 7.0, 1),
            "is_urgent": delta < 7
        }
    except ValueError:
        return {"days": 0, "weeks": 0.0, "is_urgent": False}

@tool
def validate_schedule(sessions_per_week: int, total_sessions_needed: int, available_weeks: float) -> dict:
    """Validate if a study schedule is feasible."""
    capacity = int(sessions_per_week * available_weeks)
    is_feasible = capacity >= total_sessions_needed
    shortfall = max(0, total_sessions_needed - capacity)
    
    recommendation = "Schedule is feasible." if is_feasible else f"Shortfall of {shortfall} sessions. Consider increasing sessions per week or duration."
    
    return {
        "is_feasible": is_feasible,
        "shortfall": shortfall,
        "recommendation": recommendation
    }
