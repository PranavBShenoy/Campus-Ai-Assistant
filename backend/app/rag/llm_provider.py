import logging
import json
from typing import Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLanguageModel
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration

from app.core.config import settings

logger = logging.getLogger('campus_ai.rag.llm_provider')


def message_content_to_text(content: Any) -> str:
    """Normalize LangChain/OpenRouter text and content-block responses."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                value = block.get("text") or block.get("content")
                parts.append(str(value) if value is not None else json.dumps(block, ensure_ascii=False))
            else:
                parts.append(str(block))
        return "\n".join(part for part in parts if part)
    if isinstance(content, dict):
        value = content.get("text") or content.get("content")
        return str(value) if value is not None else json.dumps(content, ensure_ascii=False)
    return str(content)

class MockLLM(BaseChatModel):
    _llm_type: str = "mock_llm"

    @property
    def _llm_type(self) -> str:
        return "mock"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        response_text = (
            "This is a demo mode academic response. The system is operating in DEMO MODE "
            "with a Mock LLM. I can help with general academic advice, study plans, and "
            "navigating college life. (Please configure real API keys in your .env file "
            "for full functionality)."
        )
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=response_text))])

def get_llm(task: str = "chat", temperature: float = 0.7) -> BaseLanguageModel:
    if settings.DEMO_MODE:
        logger.info("Using MockLLM (DEMO_MODE=True)")
        return MockLLM()
        
    if settings.is_openrouter and settings.OPENROUTER_API_KEY:
        if task == "study_plan" and settings.OPENROUTER_STUDY_PLAN_MODEL:
            model_name = settings.OPENROUTER_STUDY_PLAN_MODEL
        elif task == "review" and settings.OPENROUTER_REVIEW_MODEL:
            model_name = settings.OPENROUTER_REVIEW_MODEL
        else:
            model_name = settings.OPENROUTER_MODEL
            
        logger.info(f"Using OpenRouter (model: {model_name}, task: {task})")
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
            model=model_name,
            temperature=temperature,
            timeout=60,
            max_retries=1,
        )
        
    logger.error("LLM not configured properly.")
    raise ValueError('LLM not configured. Set OPENROUTER_API_KEY in .env')
