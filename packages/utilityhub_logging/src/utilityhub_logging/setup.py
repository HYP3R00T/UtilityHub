from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path

from utilityhub_logging.cleanup import cleanup_logging, mark_handler
from utilityhub_logging.context import ContextFilter, bind_context
from utilityhub_logging.formatters import JsonFormatter, PlainTextFormatter
from utilityhub_logging.paths import resolve_logs_path
from utilityhub_logging.types import LogFormat, LogPathConvention, ManagedHandlerKind


def configure_app_logging(
    app_name: str,
    *,
    level: int | str = "INFO",
    logs_path: str | Path | None = None,
    default_convention: LogPathConvention | str = LogPathConvention.PLATFORM,
    console: bool = True,
    log_format: LogFormat | str = LogFormat.PLAIN,
    logger: logging.Logger | None = None,
    propagate: bool = False,
) -> Path:
    target_logger = logging.getLogger() if logger is None else logger
    target_logger.setLevel(_normalize_level(level))
    target_logger.propagate = propagate

    cleanup_logging(target_logger, kind=ManagedHandlerKind.APP)

    resolved_logs_path = resolve_logs_path(
        app_name=app_name,
        logs_path=logs_path,
        default_convention=default_convention,
    )
    session_id = uuid.uuid4().hex[:8]
    timestamp = _utc_now_stamp()
    file_path = resolved_logs_path / f"{_slugify(app_name)}-{timestamp}-{session_id}.log"

    formatter = _build_formatter(log_format)
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setLevel(_normalize_level(level))
    file_handler.setFormatter(formatter)
    file_handler.addFilter(ContextFilter())
    target_logger.addHandler(mark_handler(file_handler, kind=ManagedHandlerKind.APP, file_path=file_path))

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(_normalize_level(level))
        console_handler.setFormatter(formatter)
        console_handler.addFilter(ContextFilter())
        target_logger.addHandler(mark_handler(console_handler, kind=ManagedHandlerKind.APP))

    bind_context(app_name=app_name, session_id=session_id)
    return file_path


def _build_formatter(log_format: LogFormat | str) -> logging.Formatter:
    selected = LogFormat(log_format)
    if selected is LogFormat.JSON:
        return JsonFormatter()
    return PlainTextFormatter()


def _normalize_level(level: int | str) -> int:
    if isinstance(level, int):
        return level
    normalized = logging.getLevelName(level.upper())
    if isinstance(normalized, int):
        return normalized
    msg = f"Unsupported log level: {level!r}"
    raise ValueError(msg)


def _utc_now_stamp() -> str:
    return datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")


def _slugify(value: str) -> str:
    chars = [char.lower() if char.isalnum() else "-" for char in value.strip()]
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "log"
