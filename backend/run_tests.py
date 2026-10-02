import sys
import os
import asyncio
sys.path.append(".")
    
from app.core.config import settings
settings.LLM_PROVIDER = "openrouter"
settings.OPENROUTER_API_KEY = "sk-or-v1-dummykey"

from app.rag.llm_provider import get_llm
from langchain_core.messages import HumanMessage

async def main():
    try:
        llm = get_llm(task="chat")
        print(f"Testing model: {llm.model_name}")
        response = await llm.ainvoke([HumanMessage(content="Hello!")])
        print("Response received:", response.content)
    except Exception as e:
        print("API Call Failed:", type(e).__name__, "-", e)

asyncio.run(main())
