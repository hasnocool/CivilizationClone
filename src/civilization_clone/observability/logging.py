"""Structured runtime logging helpers for diagnostics and support."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

_RESERVED = frozenset(
    {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
    }
)


class JsonLogFormatter(logging.Formatter):
    """Format operational log records as compact JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in _RESERVED:
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                payload[key] = value
            else:
                payload[key] = repr(value)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def configure_logging(
    *,
    level: int | str = logging.INFO,
    json_output: bool = False,
    handler: logging.Handler | None = None,
) -> logging.Logger:
    """Configure and return the project root logger without touching engine state."""
    logger = logging.getLogger("civilization_clone")
    logger.handlers.clear()
    logger.setLevel(level)
    logger.propagate = False

    selected_handler = handler or logging.StreamHandler()
    selected_handler.setFormatter(
        JsonLogFormatter()
        if json_output
        else logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(selected_handler)
    return logger


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    context: Mapping[str, str | int | float | bool | None] | None = None,
) -> None:
    """Emit a structured operational log record with correlation context."""
    logger.log(level, message, extra=dict(context or {}))
