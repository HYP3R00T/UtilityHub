from __future__ import annotations

import contextvars
import logging
from collections.abc import Mapping
from contextlib import AbstractContextManager
from contextvars import Token
from typing import Any

_LOG_CONTEXT: contextvars.ContextVar[dict[str, Any] | None] = contextvars.ContextVar(
    "utilityhub_logging_context",
    default=None,
)

_RESERVED_LOG_KEYS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "message",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


def get_context() -> dict[str, Any]:
    return dict(_LOG_CONTEXT.get() or {})


class BoundContext(AbstractContextManager["BoundContext"]):
    def __init__(self, token: Token[dict[str, Any]]) -> None:
        self._token = token
        self._closed = False

    def __enter__(self) -> BoundContext:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        if not self._closed:
            _LOG_CONTEXT.reset(self._token)
            self._closed = True


def bind_context(**context: Any) -> BoundContext:
    current = dict(_LOG_CONTEXT.get() or {})
    current.update({key: value for key, value in context.items() if value is not None})
    return BoundContext(_LOG_CONTEXT.set(current))


def clear_context() -> None:
    _LOG_CONTEXT.set({})


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        merged_context = get_context()
        extra_context = getattr(record, "utilityhub_context", None)
        if isinstance(extra_context, Mapping):
            merged_context.update(extra_context)
        record.utilityhub_context = merged_context
        for key, value in merged_context.items():
            if key.isidentifier() and key not in _RESERVED_LOG_KEYS:
                setattr(record, key, value)
        return True
