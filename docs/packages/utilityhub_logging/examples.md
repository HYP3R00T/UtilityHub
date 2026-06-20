---
icon: lucide/lightbulb
---

# Examples

This page shows complete, realistic examples for `utilityhub_logging` so teams can see how the package fits into larger systems.

## What These Examples Show

The examples below focus on the kinds of situations where logging becomes messy if every application invents its own setup:

- a CLI that needs one log file per run
- a worker that needs structured logs and job context
- a service that wants both app-level and request-level logs

## Example 1: CLI Application With A Session Log

This is a good fit for local tools, internal developer utilities, and admin commands.

```python
import logging

from utilityhub_logging import configure_app_logging, cleanup_logging


def main() -> None:
    log_file = configure_app_logging(
        app_name="data-tool",
        level="INFO",
        console=True,
    )

    logger = logging.getLogger("data_tool")
    logger.info("CLI started")
    logger.info("Writing detailed logs to %s", log_file)

    try:
        logger.info("Running command")
        # do work here
        logger.info("Command completed")
    finally:
        cleanup_logging()
```

Why this works well:

- users still see console output
- each invocation gets its own session log file
- cleanup is explicit at shutdown

## Example 2: Background Worker With Structured Logs

This pattern works well when logs are collected by a platform or aggregation system.

```python
import logging

from utilityhub_logging import LogFormat, bind_context, cleanup_logging, configure_app_logging


def run_worker() -> None:
    configure_app_logging(
        app_name="image-worker",
        level="INFO",
        console=False,
        log_format=LogFormat.JSON,
    )

    logger = logging.getLogger("image_worker")

    for job in get_jobs():
        with bind_context(job_id=job.id, queue="images", worker="worker-1"):
            logger.info("Job received")
            try:
                process_job(job)
                logger.info("Job completed")
            except Exception:
                logger.exception("Job failed")

    cleanup_logging()
```

Why this works well:

- JSON output is easier for machines to parse
- job-level metadata is attached consistently
- the worker does not need to manually repeat IDs in every message

## Example 3: Service With App Logs And Request Scope Logs

This is useful when you want a stable process-level log plus isolated files for especially important units of work.

```python
import logging

from utilityhub_logging import (
    begin_scope_logging,
    bind_context,
    cleanup_logging,
    configure_app_logging,
    end_scope_logging,
)


app_logger = logging.getLogger("api")


def startup() -> None:
    configure_app_logging(
        app_name="orders-api",
        logger=app_logger,
        level="INFO",
        console=True,
    )


def handle_request(request_id: str, user_id: str) -> None:
    request_logger, request_log_file = begin_scope_logging(
        app_name="orders-api",
        scope_type="request",
        scope_id=request_id,
        level="INFO",
    )

    try:
        with bind_context(request_id=request_id, user_id=user_id, subsystem="orders"):
            app_logger.info("Request accepted")
            request_logger.info("Request log file created at %s", request_log_file)
            # handle request here
            request_logger.info("Request completed")
    finally:
        end_scope_logging(request_logger)


def shutdown() -> None:
    cleanup_logging(close_all_loggers=True)
```

Why this works well:

- app logs still capture overall process behavior
- each request can also have its own dedicated file when needed
- request metadata stays consistent across both loggers

## Example 4: Safer Non-Root Logger Setup In A Larger System

In bigger applications, you may want logging setup isolated to one part of the system.

```python
import logging

from utilityhub_logging import configure_app_logging


payments_logger = logging.getLogger("platform.payments")

log_file = configure_app_logging(
    app_name="platform",
    logger=payments_logger,
    level="DEBUG",
    console=False,
    propagate=False,
)

payments_logger.debug("Payments subsystem configured")
```

Why this works well:

- only the targeted logger is configured
- propagation is disabled to avoid duplicate handling upstream
- subsystem-level logs are easier to isolate

## Choosing Between These Patterns

- Use the CLI pattern when one human-triggered run should produce one log file.
- Use the worker pattern when logs are structured and machine-consumed.
- Use the service pattern when you need both process-level and operation-level visibility.
- Use the subsystem logger pattern when only part of a larger application should own a logging setup.

## Local Demo Script

To validate the package behavior before publishing, run:

```bash
/workspaces/UtilityHub/.venv/bin/python examples/demo_utilityhub_logging/main.py
```

This demo creates temporary log files, writes app-session and scoped records, and then prints the resulting files so you can inspect the output directly.

[← Back to Documentation](./index.md)
