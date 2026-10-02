from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain.schema import BaseMessage

class AcademicState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    user_id: str
    session_id: str
    conversation_id: Optional[str]
    mode: str
    intent: Optional[str]
    needs_retrieval: bool
    is_follow_up: bool
    standalone_query: Optional[str]
    retrieved_sources: list[dict]
    context_string: Optional[str]
    generated_response: Optional[str]
    sources: list[dict]
    is_grounded: Optional[bool]
    groundedness_score: Optional[float]
    study_plan_data: Optional[dict]
    error: Optional[str]
    processing_notes: list[str]

class StudyPlanState(TypedDict):
    subjects: list[dict]
    constraints: dict
    existing_plan: Optional[dict]
    modification_instruction: Optional[str]
    generated_plan: Optional[dict]
    validation_errors: list[str]
    is_valid: bool
    today: str
    retries: int
