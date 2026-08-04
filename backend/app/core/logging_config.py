"""
logging_config.py — Configures structured (JSON) logging for the
whole app. Call setup_logging() once, at startup, in main.py.
"""

import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import settings


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)

    # Each log line becomes one JSON object, with these fields always
    # present -- timestamp, level, logger name, and the message itself.
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    # Quiet down noisy third-party loggers so our own logs aren't
    # drowned out (recall today's LangGraph deprecation warning, etc.)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
