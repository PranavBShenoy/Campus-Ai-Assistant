import sys
import os
sys.path.append(".")
os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-dummykey"

from app.rag.llm_provider import get_llm
from app.core.config import settings

# Force reload settings
settings.OPENROUTER_API_KEY = "sk-or-v1-dummykey"

try:
    llm = get_llm(task="chat")
    print(f"Instantiated: {llm.model_name} at {llm.openai_api_base}")
except Exception as e:
    print(f"Error: {e}")

try:
    settings.OPENROUTER_STUDY_PLAN_MODEL = "anthropic/claude-3-haiku"
    llm = get_llm(task="study_plan")
    print(f"Instantiated: {llm.model_name} at {llm.openai_api_base}")
except Exception as e:
    print(f"Error: {e}")
