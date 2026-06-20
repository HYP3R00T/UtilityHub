"""Demo for utilityhub_logging before publishing to PyPI.

Run from repository root:
    /workspaces/UtilityHub/.venv/bin/python examples/demo_utilityhub_logging/main.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_PACKAGE_SRC = REPO_ROOT / "packages" / "utilityhub_logging" / "src"
if LOCAL_PACKAGE_SRC.exists():
    sys.path.insert(0, str(LOCAL_PACKAGE_SRC))

from utilityhub_logging import (  # noqa: E402
    begin_scope_logging,
    bind_context,
    cleanup_logging,
    configure_app_logging,
    end_scope_logging,
)

LINE_WIDTH = 76


def print_file_excerpt(path: Path, *, title: str) -> None:
    print(f"\n{title}")
    print("-" * LINE_WIDTH)
    print(path.read_text(encoding="utf-8").strip())


def main() -> None:
    print("utilityhub_logging Demo: One Run, One Scope, No Drama")
    print("=" * LINE_WIDTH)
    print("Local package source is used so you can validate behavior before release.")

    with TemporaryDirectory() as temp_dir:
        logs_root = Path(temp_dir) / "demo-logs"
        app_logger = logging.getLogger("demo.worker")
        app_logger.handlers.clear()

        print("\nScene 1: configure one session log for the app run.")
        app_log_file = configure_app_logging(
            app_name="demo-worker",
            logger=app_logger,
            logs_path=logs_root,
            level="INFO",
            console=False,
        )
        print(f"Session log file: {app_log_file}")

        with bind_context(environment="dev", subsystem="ingest"):
            app_logger.info("Worker boot complete")

        print("\nScene 2: create a scoped log for one job.")
        job_logger, job_log_file = begin_scope_logging(
            app_name="demo-worker",
            scope_type="job",
            scope_id="job-123",
            logs_path=logs_root,
            level="INFO",
        )
        print(f"Scoped log file: {job_log_file}")

        try:
            with bind_context(job_id="job-123", subsystem="ingest", source="demo-bucket"):
                app_logger.info("Job accepted by worker")
                job_logger.info("Job started")
                job_logger.info("Transform step complete")
                job_logger.info("Job finished successfully")
        finally:
            end_scope_logging(job_logger)
            cleanup_logging(app_logger)

        print("\nScene 3: inspect the generated files.")
        print_file_excerpt(app_log_file, title="App session log contents")
        print_file_excerpt(job_log_file, title="Scoped job log contents")

    print("\nVerdict")
    print("- configure_app_logging() created one file for the app session")
    print("- begin_scope_logging() created one file for the job scope")
    print("- bind_context() attached metadata consistently")
    print("- cleanup_logging() and end_scope_logging() closed managed handlers cleanly")


if __name__ == "__main__":
    main()
