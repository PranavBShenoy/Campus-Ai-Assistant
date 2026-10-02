from pydantic import BaseModel
from typing import List, Optional
from pydantic import Field

class EvaluationQuestion(BaseModel):
    question: str
    category: str
    expected_has_answer: bool = True

class RunEvaluationRequest(BaseModel):
    questions: List[EvaluationQuestion] = Field(min_length=1)
    session_id: Optional[str] = None

class EvaluationResult(BaseModel):
    question: str
    category: str
    basic_llm_response: str
    rag_response: str
    sources: List[dict]
    basic_latency_ms: float
    rag_latency_ms: float
    has_citations: bool
    groundedness_score: Optional[float] = None
    retrieval_count: int

class EvaluationRunResponse(BaseModel):
    run_id: str
    results: List[EvaluationResult]
    avg_rag_latency: float
    avg_basic_latency: float
    avg_groundedness: float
    total_questions: int
    questions_with_citations: int

