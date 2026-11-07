"""Centralized structured logging with console streaming and JSON-Lines output."""

import json
import logging
from pathlib import Path
from typing import Any, Dict
from core.config import config

class JsonLinesFormatter(logging.Formatter):
    """Formats log records as structured JSON lines for auditability."""
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

def get_logger(name: str) -> logging.Logger:
    """Returns a pre-configured logger with console and file handlers.

    Args:
        name: Name of the logger, typically __name__.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        config.logs_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(config.logs_dir / "eval.jsonl", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JsonLinesFormatter())
        logger.addHandler(file_handler)
    return logger
