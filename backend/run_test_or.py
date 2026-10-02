import sys
import os
import asyncio
sys.path.append(".")
    
from app.rag.llm_provider import get_llm
from langchain_core.messages import HumanMessage
from app.core.config import settings

async def main():
    try:
        print(f"Provider: {settings.LLM_PROVIDER}")
        print(f"OpenRouter key length: {len(settings.OPENROUTER_API_KEY) if settings.OPENROUTER_API_KEY else 0}")
        llm = get_llm(task="chat")
        print(f"Testing model: {llm.model_name}")
        response = await llm.ainvoke([HumanMessage(content="Hello! Are you working?")])
        print("Response received:", response.content)
    except Exception as e:
        print("API Call Failed:", type(e).__name__, "-", e)

asyncio.run(main())
