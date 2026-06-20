from __future__ import annotations

import logging
from pathlib import Path

from utilityhub_logging.context import clear_context
from utilityhub_logging.types import ManagedHandlerKind

_MANAGED_HANDLER_FLAG = "_utilityhub_managed"
_MANAGED_HANDLER_KIND = "_utilityhub_kind"
_MANAGED_HANDLER_PATH = "_utilityhub_log_path"


def mark_handler(
    handler: logging.Handler,
    *,
    kind: ManagedHandlerKind,
    file_path: Path | None = None,
) -> logging.Handler:
    setattr(handler, _MANAGED_HANDLER_FLAG, True)
    setattr(handler, _MANAGED_HANDLER_KIND, kind.value)
    setattr(handler, _MANAGED_HANDLER_PATH, file_path)
    return handler


def is_managed_handler(handler: logging.Handler, *, kind: ManagedHandlerKind | None = None) -> bool:
    if not getattr(handler, _MANAGED_HANDLER_FLAG, False):
        return False
    if kind is None:
        return True
    return getattr(handler, _MANAGED_HANDLER_KIND, None) == kind.value


def cleanup_logging(
    logger: logging.Logger | None = None,
    *,
    kind: ManagedHandlerKind | None = None,
    close_all_loggers: bool = False,
) -> None:
    if close_all_loggers:
        logger_dict = logging.root.manager.loggerDict
        for candidate in [logging.getLogger()] + [
            value for value in logger_dict.values() if isinstance(value, logging.Logger)
        ]:
            cleanup_logging(candidate, kind=kind)
        clear_context()
        return

    target = logging.getLogger() if logger is None else logger
    handlers = list(target.handlers)
    for handler in handlers:
        if not is_managed_handler(handler, kind=kind):
            continue
        target.removeHandler(handler)
        try:
            handler.flush()
        finally:
            handler.close()
