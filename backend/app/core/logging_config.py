import logging
import sys
from app.core.config import settings

def setup_logging():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    formatter = logging.Formatter(
        "\033[36m%(asctime)s\033[0m | \033[1;32m%(levelname)-8s\033[0m | \033[35m%(name)s\033[0m - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(console_handler)

    # Disable spammy logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Configure specific loggers
    logging.getLogger("campus_ai.api").setLevel(log_level)
    logging.getLogger("campus_ai.rag").setLevel(log_level)
    logging.getLogger("campus_ai.graph").setLevel(log_level)
