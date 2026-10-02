import sys
import os
import asyncio
sys.path.append(".")
    
# Provide dummy if not present
if not os.environ.get("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-dummykey"

from app.core.config import settings
settings.LLM_PROVIDER = "openrouter"
settings.OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

from app.rag.llm_provider import get_llm
from app.tools.calculator import days_until_exam
from langchain_core.messages import HumanMessage

async def main():
    try:
        llm = get_llm(task="chat")
        print(f"Testing model: {llm.model_name}")
        llm_with_tools = llm.bind_tools([days_until_exam])
        response = await llm_with_tools.ainvoke([HumanMessage(content="How many days from 2026-10-02 to 2026-12-01?")])
        print("Response received:", response.content)
        if response.tool_calls:
            print("Tool calls generated:", response.tool_calls)
    except Exception as e:
        print("API Call Failed:", type(e).__name__, "-", e)

asyncio.run(main())
