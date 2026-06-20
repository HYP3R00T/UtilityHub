"""Composable logging utilities built on Python's standard library logging package."""

from utilityhub_logging.cleanup import cleanup_logging
from utilityhub_logging.context import bind_context
from utilityhub_logging.formatters import JsonFormatter, PlainTextFormatter
from utilityhub_logging.paths import resolve_logs_path
from utilityhub_logging.scopes import begin_scope_logging, end_scope_logging
from utilityhub_logging.setup import configure_app_logging
from utilityhub_logging.types import LogFormat, LogPathConvention

__all__: list[str] = [
    "JsonFormatter",
    "LogFormat",
    "LogPathConvention",
    "PlainTextFormatter",
    "begin_scope_logging",
    "bind_context",
    "cleanup_logging",
    "configure_app_logging",
    "end_scope_logging",
    "resolve_logs_path",
]


def main() -> None:
    print("utilityhub-logging: import and configure via `configure_app_logging()`")
