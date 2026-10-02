import sys
import os
import asyncio
sys.path.append(".")
from app.core.config import settings

# Only test LangSmith if user turned it on
if str(settings.LANGSMITH_TRACING).lower() == "true":
    print("LangSmith tracing is ENABLED in config.")
    print("LANGCHAIN_TRACING_V2:", os.environ.get("LANGCHAIN_TRACING_V2"))
    print("LANGCHAIN_PROJECT:", os.environ.get("LANGCHAIN_PROJECT"))
else:
    print("LangSmith tracing is DISABLED in config.")
