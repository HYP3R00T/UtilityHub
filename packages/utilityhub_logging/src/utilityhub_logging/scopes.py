from __future__ import annotations

import logging
from pathlib import Path

from utilityhub_logging.cleanup import cleanup_logging, mark_handler
from utilityhub_logging.context import ContextFilter, bind_context
from utilityhub_logging.paths import resolve_logs_path
from utilityhub_logging.setup import _build_formatter, _normalize_level, _slugify, _utc_now_stamp
from utilityhub_logging.types import LogFormat, LogPathConvention, ManagedHandlerKind


def begin_scope_logging(
    scope_type: str,
    scope_id: str,
    *,
    app_name: str,
    level: int | str = "INFO",
    logs_path: str | Path | None = None,
    default_convention: LogPathConvention | str = LogPathConvention.PLATFORM,
    log_format: LogFormat | str = LogFormat.PLAIN,
    logger: logging.Logger | None = None,
    propagate: bool = False,
) -> tuple[logging.Logger, Path]:
    if not scope_type.strip():
        msg = "scope_type must be a non-empty string"
        raise ValueError(msg)
    if not scope_id.strip():
        msg = "scope_id must be a non-empty string"
        raise ValueError(msg)

    target_logger = logger or logging.getLogger(f"{app_name}.{scope_type}.{scope_id}")
    target_logger.setLevel(_normalize_level(level))
    target_logger.propagate = propagate

    cleanup_logging(target_logger, kind=ManagedHandlerKind.SCOPE)

    root_logs_path = resolve_logs_path(
        app_name=app_name,
        logs_path=logs_path,
        default_convention=default_convention,
    )
    scope_logs_path = root_logs_path / "scopes" / _slugify(scope_type)
    scope_logs_path.mkdir(parents=True, exist_ok=True)
    file_path = scope_logs_path / f"{_slugify(scope_id)}-{_utc_now_stamp()}.log"

    handler = logging.FileHandler(file_path, encoding="utf-8")
    handler.setLevel(_normalize_level(level))
    handler.setFormatter(_build_formatter(log_format))
    handler.addFilter(ContextFilter())
    target_logger.addHandler(mark_handler(handler, kind=ManagedHandlerKind.SCOPE, file_path=file_path))

    bind_context(scope_type=scope_type, scope_id=scope_id)
    return target_logger, file_path


def end_scope_logging(logger: logging.Logger | None = None) -> None:
    cleanup_logging(logger, kind=ManagedHandlerKind.SCOPE)
