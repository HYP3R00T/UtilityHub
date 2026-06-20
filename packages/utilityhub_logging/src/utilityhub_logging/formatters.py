from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any


def _format_timestamp(created: float) -> str:
    dt = datetime.fromtimestamp(created, tz=UTC)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


class PlainTextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = _format_timestamp(record.created)
        message = record.getMessage()
        context = getattr(record, "utilityhub_context", {})
        context_text = ""
        if context:
            pairs = " ".join(f"{key}={value}" for key, value in sorted(context.items()))
            context_text = f" [{pairs}]"

        parts = [timestamp, record.levelname, record.name, "-", message]
        rendered = " ".join(parts) + context_text

        if record.exc_info:
            rendered = f"{rendered}\n{self.formatException(record.exc_info)}"
        if record.stack_info:
            rendered = f"{rendered}\n{self.formatStack(record.stack_info)}"
        return rendered


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": _format_timestamp(record.created),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        context = getattr(record, "utilityhub_context", {})
        if context:
            payload["context"] = dict(sorted(context.items()))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)
