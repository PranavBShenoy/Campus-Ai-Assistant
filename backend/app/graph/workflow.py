from langgraph.graph import StateGraph, END
from typing import Optional
from langchain.schema import BaseMessage
from app.graph.state import AcademicState
from app.graph.nodes import (
    analyze_query, retrieve_information, generate_response,
    review_response, finalize_response,
    route_after_analysis, route_after_retrieval, route_after_generation
)

def create_academic_workflow() -> StateGraph:
    workflow = StateGraph(AcademicState)
    
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("retrieve_information", retrieve_information)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("review_response", review_response)
    workflow.add_node("finalize_response", finalize_response)
    
    workflow.set_entry_point("analyze_query")
    
    workflow.add_conditional_edges(
        "analyze_query",
        route_after_analysis,
        {
            "retrieve_information": "retrieve_information",
            "generate_response": "generate_response",
            "finalize_response": "finalize_response"
        }
    )
    
    workflow.add_edge("retrieve_information", "generate_response")
    
    workflow.add_conditional_edges(
        "generate_response",
        route_after_generation,
        {
            "review_response": "review_response",
            "finalize_response": "finalize_response"
        }
    )
    
    workflow.add_edge("review_response", "finalize_response")
    workflow.add_edge("finalize_response", END)
    
    return workflow.compile()

_workflow = None

def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = create_academic_workflow()
    return _workflow

async def run_academic_workflow(query: str, mode: str, user_id: str, session_id: Optional[str], conversation_id: Optional[str], history: list[BaseMessage]) -> dict:
    workflow = get_workflow()
    
    initial_state = {
        "messages": history,
        "user_query": query,
        "session_id": session_id, "user_id": user_id,
        "conversation_id": conversation_id,
        "mode": mode,
        "processing_notes": []
    }
    
    final_state = await workflow.ainvoke(initial_state)
    return final_state
