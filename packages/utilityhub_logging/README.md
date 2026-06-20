# utilityhub-logging

`utilityhub-logging` is a small, project-agnostic package that extends Python's
standard library `logging` module with deterministic setup and cleanup helpers.

It focuses on the repetitive parts teams tend to rebuild:

- resolving a safe logs directory
- configuring one log file per application run
- opening a scoped log for an operation
- switching between plain text and JSON output
- attaching async-safe contextual metadata
- preventing duplicate handlers and cleaning them up reliably

## Install

```bash
uv add utilityhub-logging
```

## Quick Start

```python
import logging

from utilityhub_logging import (
    LogFormat,
    begin_scope_logging,
    bind_context,
    cleanup_logging,
    configure_app_logging,
)

log_file = configure_app_logging(
    app_name="demo-app",
    level="INFO",
    console=True,
    log_format=LogFormat.PLAIN,
)

logger = logging.getLogger("demo")
with bind_context(environment="dev", subsystem="worker"):
    logger.info("Application started")

scope_logger, scope_file = begin_scope_logging(
    app_name="demo-app",
    scope_type="job",
    scope_id="job-42",
    log_format=LogFormat.JSON,
)
scope_logger.info("Running scoped operation")

cleanup_logging()
```

## Public API

- `resolve_logs_path(...)`
- `configure_app_logging(...)`
- `begin_scope_logging(...)`
- `end_scope_logging(...)`
- `bind_context(...)`
- `cleanup_logging(...)`

## Defaults

- UTF-8 file output
- timestamped log files in UTC
- platform-aware default log directories
- `~/.local/state/<app>/logs` on Linux and similar Unix systems
- `~/Library/Logs/<app>` on macOS
- `%LOCALAPPDATA%\<app>\Logs` on Windows
- no current-working-directory logging unless explicitly requested
