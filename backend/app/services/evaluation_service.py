from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import EvaluationRun
from app.schemas.evaluation import RunEvaluationRequest, EvaluationResult, EvaluationRunResponse, EvaluationQuestion
from app.graph.workflow import run_academic_workflow
from app.rag.llm_provider import get_llm, message_content_to_text
from app.prompts.academic_qa import BASIC_LLM_PROMPT
import time, uuid, logging
from langchain.schema import HumanMessage
from datetime import datetime

logger = logging.getLogger('campus_ai.api')

class EvaluationService:
    async def run_evaluation(self, request: RunEvaluationRequest, user_id: str, db: AsyncSession) -> EvaluationRunResponse:
        llm = get_llm(task="chat")
        results = []
        
        start_time_total = time.time()
        run_id = str(uuid.uuid4())
        
        for q in request.questions:
            # 1. Basic LLM
            start_basic = time.time()
            basic_prompt = BASIC_LLM_PROMPT.format(query=q.question)
            try:
                basic_response = await llm.ainvoke([HumanMessage(content=basic_prompt)])
                basic_content = message_content_to_text(basic_response.content)
            except Exception as e:
                logger.error(f"Basic LLM error: {e}")
                basic_content = "The basic model could not answer this question."
            basic_latency = float((time.time() - start_basic) * 1000)
            
            # 2. RAG
            start_rag = time.time()
            rag_result_state = await run_academic_workflow(
                query=q.question,
                mode='academic_rag',
                user_id=user_id,
                session_id=request.session_id,
                conversation_id=None,
                history=[]
            )
            rag_latency = float((time.time() - start_rag) * 1000)
            
            sources = rag_result_state.get('sources', [])
            has_citations = len(sources) > 0
            groundedness_score = rag_result_state.get('groundedness_score', 0.0)
            retrieval_count = len(rag_result_state.get('retrieved_sources', []))
            
            res = EvaluationResult(
                question=q.question,
                category=q.category,
                basic_llm_response=basic_content,
                rag_response=rag_result_state.get('generated_response', 'Error'),
                sources=sources,
                has_citations=has_citations,
                groundedness_score=groundedness_score,
                basic_latency_ms=basic_latency,
                rag_latency_ms=rag_latency,
                retrieval_count=retrieval_count
            )
            results.append(res)
            
            # Save to DB
            eval_run = EvaluationRun(
                id=str(uuid.uuid4()),
                user_id=user_id,
                question=q.question,
                basic_llm_response=res.basic_llm_response,
                rag_response=res.rag_response,
                sources_json=sources,
                basic_latency_ms=res.basic_latency_ms,
                rag_latency_ms=res.rag_latency_ms,
                groundedness_score=res.groundedness_score,
                has_citations=res.has_citations,
            )
            db.add(eval_run)
            
        await db.commit()
        
        # Aggregate stats
        avg_basic_latency = sum(r.basic_latency_ms for r in results) / len(results) if results else 0.0
        avg_rag_latency = sum(r.rag_latency_ms for r in results) / len(results) if results else 0.0
        avg_groundedness = sum(r.groundedness_score or 0.0 for r in results) / len(results) if results else 0.0
        questions_with_citations = sum(1 for r in results if r.has_citations)
        
        return EvaluationRunResponse(
            run_id=run_id,
            results=results,
            avg_rag_latency=avg_rag_latency,
            avg_basic_latency=avg_basic_latency,
            avg_groundedness=avg_groundedness,
            total_questions=len(results),
            questions_with_citations=questions_with_citations
        )
