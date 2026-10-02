import json
import logging
from datetime import date
from langchain.schema import HumanMessage, SystemMessage
from app.graph.state import AcademicState
from app.rag.llm_provider import get_llm, message_content_to_text
from app.rag.retriever import RAGRetriever
from app.prompts.academic_qa import (
    ACADEMIC_RAG_PROMPT, BASIC_LLM_PROMPT, QUERY_ANALYSIS_PROMPT,
    RESPONSE_REVIEW_PROMPT, UNKNOWN_ANSWER_PROMPT
)
from app.core.config import settings

logger = logging.getLogger("campus_ai.graph")


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.startswith("json"):
                inner = inner[4:]
            return inner.strip()
    return text


def _parse_json_object(text: str) -> dict:
    cleaned = _strip_json_fences(text)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise
        value = json.loads(cleaned[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("The model response must be a JSON object.")
    return value


async def analyze_query(state: AcademicState) -> dict:
    logger.debug("Entering analyze_query")
    updates = {"processing_notes": list(state.get("processing_notes", [])) + ["Analyzed query"]}
    try:
        llm = get_llm(task="chat", temperature=0.0)
        response = await llm.ainvoke([
            SystemMessage(content=QUERY_ANALYSIS_PROMPT),
            HumanMessage(content=state["user_query"])
        ])
        raw = _strip_json_fences(message_content_to_text(response.content))
        try:
            parsed = _parse_json_object(raw)
        except (json.JSONDecodeError, ValueError):
            parsed = {"intent": "academic_qa", "needs_retrieval": True,
                      "is_follow_up": False, "standalone_query": state["user_query"]}
        updates["intent"] = parsed.get("intent", "academic_qa")
        updates["needs_retrieval"] = bool(parsed.get("needs_retrieval", True))
        updates["is_follow_up"] = bool(parsed.get("is_follow_up", False))
        updates["standalone_query"] = parsed.get("standalone_query") or state["user_query"]
        if state.get("mode") == "academic_rag":
            # Academic RAG never silently bypasses the user's documents.
            updates["needs_retrieval"] = True
        elif updates["intent"] in ["study_planning", "out_of_scope"]:
            updates["needs_retrieval"] = False
    except Exception as e:
        logger.error(f"Error in analyze_query: {e}", exc_info=True)
        updates["intent"] = "academic_qa"
        updates["needs_retrieval"] = True
        updates["is_follow_up"] = False
        updates["standalone_query"] = state["user_query"]
    return updates


async def retrieve_information(state: AcademicState) -> dict:
    logger.debug("Entering retrieve_information")
    updates = {"processing_notes": list(state.get("processing_notes", [])) + ["Performed retrieval"]}
    if state.get("mode") == "basic_llm" or not state.get("needs_retrieval", False):
        updates["retrieved_sources"] = []
        updates["context_string"] = ""
        return updates
    try:
        retriever = RAGRetriever()
        query = state.get("standalone_query") or state["user_query"]
        source_refs = await retriever.retrieve(query, state["user_id"])
        context_string = retriever.build_context_string(source_refs)
        sources_as_dicts = [
            {"document_id": s.document_id, "document_name": s.document_name,
             "excerpt": s.excerpt[:2000], "page_number": s.page_number,
             "chunk_id": s.chunk_id, "relevance_score": float(s.relevance_score)}
            for s in source_refs
        ]
        updates["retrieved_sources"] = sources_as_dicts
        updates["context_string"] = context_string
        logger.info(f"Retrieved {len(source_refs)} sources for: {query[:80]}")
    except Exception as e:
        logger.error(f"Error in retrieve_information: {e}", exc_info=True)
        raise RuntimeError("Knowledge base retrieval failed.") from e
    return updates


async def _generate_study_plan_response(state: AcademicState) -> str:
    try:
        from app.graph.study_plan_workflow import generate_study_plan
        llm = get_llm(task="chat")
        today_str = date.today().isoformat()
        prompt = (
            "Extract study plan information from this message. Return ONLY valid JSON with keys: "
            "subjects (list of objects with: name, topics (list of strings), exam_date (YYYY-MM-DD), "
            "difficulty (easy/medium/hard), priority (low/medium/high), current_level (beginner/intermediate/advanced)), "
            "constraints (object with: daily_hours (float), preferred_time (morning/afternoon/evening/flexible), "
            "break_frequency_minutes (int), weekly_off_days (list of ints 0-6), start_date (YYYY-MM-DD)). "
            "Use sensible defaults for any missing information. "
            "Message: " + state["user_query"]
        )
        raw_resp = await llm.ainvoke([HumanMessage(content=prompt)])
        plan_input = _parse_json_object(message_content_to_text(raw_resp.content))
        result = await generate_study_plan(
            subjects=plan_input.get("subjects", []),
            constraints=plan_input.get("constraints", {}),
            today=today_str
        )
        n = len(result.get("sessions", []))
        start = result.get("start_date", today_str)
        end = result.get("end_date", today_str)
        return (
            f"I have created a study plan with **{n} sessions** "
            f"running from **{start}** to **{end}**. "
            "Visit the **Study Planner** page to view, modify, and track your schedule."
        )
    except Exception as e:
        logger.warning(f"Study plan node fallback: {e}")
        return (
            "I can help you build a study plan! Please visit the **Study Planner** page "
            "where you can enter your subjects, exam dates, and daily availability, "
            "and I will generate a personalized schedule."
        )


async def generate_response(state: AcademicState) -> dict:
    logger.debug("Entering generate_response")
    updates = {"processing_notes": list(state.get("processing_notes", [])) + ["Generated response"]}
    try:
        if state.get("intent") == "study_planning":
            updates["generated_response"] = await _generate_study_plan_response(state)
            return updates
        llm = get_llm(task="chat")
        context_string = state.get("context_string", "")
        mode = state.get("mode", "basic_llm")
        has_context = (
            bool(context_string) and
            context_string.strip() != "" and
            context_string != "No relevant documents found."
        )
        if mode == "academic_rag":
            if has_context:
                base_messages = [
                    SystemMessage(content=ACADEMIC_RAG_PROMPT),
                    SystemMessage(content="Retrieved Context from College Documents:\n\n" + context_string),
                ]
            else:
                updates["generated_response"] = (
                    "I could not find relevant information in your indexed documents. "
                    "Try rephrasing the question or upload the relevant PDF, DOCX, or TXT file."
                )
                return updates
        else:
            base_messages = [SystemMessage(content=BASIC_LLM_PROMPT)]
        history_msgs = list(state.get("messages", []))
        final_human = HumanMessage(content=state["user_query"])
        all_messages = base_messages + history_msgs[-6:] + [final_human]
        response = await llm.ainvoke(all_messages)
        updates["generated_response"] = message_content_to_text(response.content)
    except Exception as e:
        logger.error(f"Error in generate_response: {e}", exc_info=True)
        raise RuntimeError("LLM response generation failed.") from e
    return updates


async def review_response(state: AcademicState) -> dict:
    logger.debug("Entering review_response")
    updates = {"processing_notes": list(state.get("processing_notes", [])) + ["Reviewed response"]}
    if state.get("mode") == "basic_llm":
        updates["is_grounded"] = True
        updates["groundedness_score"] = 1.0
        return updates
    try:
        llm = get_llm(task="review", temperature=0.0)
        review_input = (
            "Response:\n" + state.get("generated_response", "") +
            "\n\nContext:\n" + state.get("context_string", "[No context]")
        )
        response = await llm.ainvoke([
            SystemMessage(content=RESPONSE_REVIEW_PROMPT),
            HumanMessage(content=review_input)
        ])
        raw = _strip_json_fences(message_content_to_text(response.content))
        try:
            parsed = _parse_json_object(raw)
        except (json.JSONDecodeError, ValueError):
            parsed = {"is_grounded": False, "groundedness_score": 0.0, "has_fabrication": False}
        if parsed.get("has_fabrication"):
            updates["generated_response"] = (
                "Warning: This response may not be fully grounded in available documents.\n\n"
                + state.get("generated_response", "")
            )
        updates["is_grounded"] = bool(parsed.get("is_grounded", True))
        updates["groundedness_score"] = float(parsed.get("groundedness_score", 0.75))
    except Exception as e:
        logger.warning(f"review_response skipped: {e}")
        updates["is_grounded"] = False
        updates["groundedness_score"] = 0.0
        updates["processing_notes"].append("Response review failed")
    return updates


async def finalize_response(state: AcademicState) -> dict:
    logger.debug("Entering finalize_response")
    updates = {"processing_notes": list(state.get("processing_notes", [])) + ["Finalized response"]}
    try:
        updates["sources"] = state.get("retrieved_sources", [])
        if not state.get("generated_response"):
            updates["generated_response"] = "I could not generate a response. Please try again."
    except Exception as e:
        logger.error(f"Error in finalize_response: {e}", exc_info=True)
    return updates


def route_after_analysis(state: AcademicState) -> str:
    if state.get("error"):
        return "finalize_response"
    if state.get("mode") == "academic_rag" and state.get("needs_retrieval", True):
        return "retrieve_information"
    return "generate_response"


def route_after_retrieval(state: AcademicState) -> str:
    return "generate_response"


def route_after_generation(state: AcademicState) -> str:
    if state.get("error"):
        return "finalize_response"
    return "review_response"
