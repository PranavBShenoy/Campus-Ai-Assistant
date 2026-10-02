import json
def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text.strip()

def _parse_json_object(text: str) -> dict:
    cleaned = _strip_json_fences(text)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find('{'), cleaned.rfind('}')
        if start < 0 or end <= start:
            raise
        value = json.loads(cleaned[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("The model response must be a JSON object.")
    if not isinstance(value.get("sessions"), list):
        for key in ("study_plan", "plan", "generated_plan", "existing_plan"):
            nested = value.get(key)
            if isinstance(nested, dict) and isinstance(nested.get("sessions"), list):
                return nested
    return value
import logging
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage
from app.graph.state import StudyPlanState
from app.rag.llm_provider import get_llm, message_content_to_text
from app.prompts.study_plan import STUDY_PLAN_GENERATION_PROMPT, STUDY_PLAN_MODIFICATION_PROMPT

logger = logging.getLogger('campus_ai.graph.study_plan')

async def collect_constraints(state: StudyPlanState) -> dict:
    logger.debug("Entering collect_constraints")
    updates = {}
    errors = []
    
    try:
        start_date = datetime.fromisoformat(str(state.get("constraints", {}).get("start_date"))).date()
        if start_date < datetime.fromisoformat(str(state["today"])).date():
            errors.append("The study plan start date cannot be in the past.")
    except (TypeError, ValueError):
        errors.append("A valid study plan start date is required.")
        start_date = None

    for subj in state.get("subjects", []):
        exam_date = subj.get("exam_date")
        if exam_date:
            try:
                parsed_exam_date = datetime.fromisoformat(str(exam_date)).date()
                if parsed_exam_date < datetime.fromisoformat(str(state["today"])).date():
                    errors.append(f"Exam date for {subj['name']} is in the past.")
                elif start_date and parsed_exam_date < start_date:
                    errors.append(f"Exam date for {subj['name']} is before the plan start date.")
            except ValueError:
                errors.append(f"Exam date for {subj.get('name', 'subject')} is invalid.")
                
    updates["validation_errors"] = errors
    return updates

async def generate_plan(state: StudyPlanState) -> dict:
    logger.debug("Entering generate_plan")
    updates = {}
    try:
        llm = get_llm(task="study_plan")
        response = await llm.ainvoke([
            SystemMessage(content=STUDY_PLAN_GENERATION_PROMPT),
            HumanMessage(content=json.dumps({"subjects": state.get("subjects"), "constraints": state.get("constraints")}))
        ])
        
        try:
            plan = _parse_json_object(message_content_to_text(response.content))
            updates["generated_plan"] = plan
            updates["validation_errors"] = []
        except (json.JSONDecodeError, ValueError, TypeError):
            updates["validation_errors"] = ["Failed to generate a valid plan structure."]
            updates["retries"] = state.get("retries", 0) + 1
            
    except Exception as e:
        logger.error(f"Error in generate_plan: {e}")
        updates["validation_errors"] = ["The AI planner did not return a usable schedule."]
        updates["retries"] = state.get("retries", 0) + 1
    return updates

async def validate_plan(state: StudyPlanState) -> dict:
    logger.debug("Entering validate_plan")
    updates = {"is_valid": True}
    errors = list(state.get("validation_errors", []))
    
    plan = state.get("generated_plan")
    if not plan:
        errors.append("No plan was generated.")
    elif not isinstance(plan.get("sessions"), list) or not plan["sessions"]:
        errors.append("The generated plan contains no study sessions.")
        
    updates["validation_errors"] = errors
    if errors:
        updates["is_valid"] = False
        
    return updates

async def modify_plan(state: StudyPlanState) -> dict:
    logger.debug("Entering modify_plan")
    updates = {}
    try:
        llm = get_llm(task="study_plan")
        response = await llm.ainvoke([
            SystemMessage(content=STUDY_PLAN_MODIFICATION_PROMPT),
            HumanMessage(content=json.dumps({
                "today": state.get("today"),
                "existing_plan": state.get("existing_plan"),
                "instruction": state.get("modification_instruction"),
            }))
        ])
        
        try:
            plan = _parse_json_object(message_content_to_text(response.content))
            updates["generated_plan"] = plan
            updates["validation_errors"] = []
        except (json.JSONDecodeError, ValueError, TypeError):
            updates["validation_errors"] = ["Failed to parse modified plan structure."]
            
    except Exception as e:
        logger.error(f"Error in modify_plan: {e}")
        updates["validation_errors"] = ["The AI planner did not return a usable schedule."]
        updates["retries"] = state.get("retries", 0) + 1
    return updates

def route_after_generate(state: StudyPlanState) -> str:
    if state.get("validation_errors") and state.get("retries", 0) < 2:
        return "generate_plan"
    return "validate_plan"

def route_after_constraints(state: StudyPlanState) -> str:
    return "validate_plan" if state.get("validation_errors") else "generate_plan"

def create_study_plan_generation_workflow() -> StateGraph:
    workflow = StateGraph(StudyPlanState)
    
    workflow.add_node("collect_constraints", collect_constraints)
    workflow.add_node("generate_plan", generate_plan)
    workflow.add_node("validate_plan", validate_plan)
    
    workflow.set_entry_point("collect_constraints")
    
    workflow.add_conditional_edges(
        "collect_constraints",
        route_after_constraints,
        {
            "generate_plan": "generate_plan",
            "validate_plan": "validate_plan",
        },
    )
    workflow.add_conditional_edges(
        "generate_plan",
        route_after_generate,
        {
            "generate_plan": "generate_plan",
            "validate_plan": "validate_plan"
        }
    )
    workflow.add_edge("validate_plan", END)
    
    return workflow.compile()

def create_study_plan_modification_workflow() -> StateGraph:
    workflow = StateGraph(StudyPlanState)
    
    workflow.add_node("modify_plan", modify_plan)
    workflow.add_node("validate_plan", validate_plan)
    
    workflow.set_entry_point("modify_plan")
    workflow.add_edge("modify_plan", "validate_plan")
    workflow.add_edge("validate_plan", END)
    
    return workflow.compile()

async def generate_study_plan(subjects: list[dict], constraints: dict, today: str) -> dict:
    workflow = create_study_plan_generation_workflow()
    state = {
        "subjects": subjects,
        "constraints": constraints,
        "today": today,
        "retries": 0,
        "validation_errors": []
    }
    result = await workflow.ainvoke(state)
    if not result.get("is_valid") or not result.get("generated_plan"):
        errors = "; ".join(result.get("validation_errors", [])) or "Study plan generation failed."
        raise ValueError(errors)
    return result["generated_plan"]

async def modify_study_plan(existing_plan: dict, instruction: str, today: str) -> dict:
    workflow = create_study_plan_modification_workflow()
    state = {
        "existing_plan": existing_plan,
        "modification_instruction": instruction,
        "today": today,
        "retries": 0,
        "validation_errors": []
    }
    result = await workflow.ainvoke(state)
    if not result.get("is_valid") or not result.get("generated_plan"):
        errors = "; ".join(result.get("validation_errors", [])) or "Study plan modification failed."
        raise ValueError(errors)
    return result["generated_plan"]





