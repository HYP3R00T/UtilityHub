from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utilityhub_logging import (
    LogFormat,
    LogPathConvention,
    begin_scope_logging,
    bind_context,
    cleanup_logging,
    configure_app_logging,
    end_scope_logging,
    resolve_logs_path,
)


def test_resolve_logs_path_uses_explicit_path(tmp_path: Path) -> None:
    logs_path = resolve_logs_path("demo-app", logs_path=tmp_path / "custom-logs")
    assert logs_path == tmp_path / "custom-logs"
    assert logs_path.exists()


def test_resolve_logs_path_supports_cwd_convention(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    logs_path = resolve_logs_path("demo-app", default_convention=LogPathConvention.CWD)
    assert logs_path == tmp_path / "logs" / "demo-app"


def test_configure_app_logging_creates_one_session_file_and_no_duplicate_handlers(tmp_path: Path) -> None:
    logger = logging.getLogger("utilityhub.test.app")
    logger.handlers.clear()

    first_path = configure_app_logging("demo-app", logs_path=tmp_path, logger=logger, console=False)
    second_path = configure_app_logging("demo-app", logs_path=tmp_path, logger=logger, console=False)

    assert first_path != second_path
    assert len(logger.handlers) == 1

    logger.info("session message")
    cleanup_logging(logger)

    assert second_path.read_text(encoding="utf-8").count("session message") == 1


def test_plain_text_logging_includes_bound_context(tmp_path: Path) -> None:
    logger = logging.getLogger("utilityhub.test.plain")
    logger.handlers.clear()

    log_file = configure_app_logging(
        "demo-app",
        logs_path=tmp_path,
        logger=logger,
        console=False,
        log_format=LogFormat.PLAIN,
    )
    with bind_context(request_id="req-123", subsystem="worker"):
        logger.info("processing")
    cleanup_logging(logger)

    contents = log_file.read_text(encoding="utf-8")
    assert "processing" in contents
    assert "request_id=req-123" in contents
    assert "subsystem=worker" in contents


def test_json_logging_includes_context_payload(tmp_path: Path) -> None:
    logger = logging.getLogger("utilityhub.test.json")
    logger.handlers.clear()

    log_file = configure_app_logging(
        "demo-app",
        logs_path=tmp_path,
        logger=logger,
        console=False,
        log_format=LogFormat.JSON,
    )
    with bind_context(user_id="u-42"):
        logger.warning("json message")
    cleanup_logging(logger)

    payload = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert payload["message"] == "json message"
    assert payload["context"]["user_id"] == "u-42"
    assert payload["context"]["app_name"] == "demo-app"


def test_begin_scope_logging_creates_scoped_file_and_end_scope_removes_handler(tmp_path: Path) -> None:
    logger, log_file = begin_scope_logging(
        scope_type="job",
        scope_id="job-123",
        app_name="demo-app",
        logs_path=tmp_path,
        log_format=LogFormat.PLAIN,
    )
    logger.info("scoped message")

    assert log_file.parent == tmp_path / "scopes" / "job"
    assert len(logger.handlers) == 1

    end_scope_logging(logger)
    assert len(logger.handlers) == 0
    assert "scoped message" in log_file.read_text(encoding="utf-8")


def test_cleanup_logging_can_close_all_managed_handlers(tmp_path: Path) -> None:
    app_logger = logging.getLogger("utilityhub.test.cleanup.app")
    scope_logger = logging.getLogger("utilityhub.test.cleanup.scope")
    app_logger.handlers.clear()
    scope_logger.handlers.clear()

    configure_app_logging("demo-app", logs_path=tmp_path, logger=app_logger, console=False)
    begin_scope_logging("task", "task-1", app_name="demo-app", logs_path=tmp_path, logger=scope_logger)

    cleanup_logging(close_all_loggers=True)

    assert app_logger.handlers == []
    assert scope_logger.handlers == []
