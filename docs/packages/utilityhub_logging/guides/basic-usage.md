# Basic Usage

## Install

```bash
uv add utilityhub-logging
```

## Configure Application Logging

```python
import logging

from utilityhub_logging import configure_app_logging

log_file = configure_app_logging(
    app_name="myapp",
    level="INFO",
    console=True,
)

logger = logging.getLogger("myapp")
logger.info("Application started")
```

`configure_app_logging()` returns the created session log file path.

If you want a full parameter-by-parameter explanation, see [App Logging Configuration](./app-logging-configuration.md).

## Configure a Specific Logger

```python
logger = logging.getLogger("myapp.worker")

log_file = configure_app_logging(
    app_name="myapp",
    logger=logger,
    level="DEBUG",
    console=False,
)
```

This is useful when you do not want to configure the root logger.

## Common Configuration Patterns

### Debug file logging without console output

```python
log_file = configure_app_logging(
    app_name="myapp",
    level="DEBUG",
    console=False,
)
```

### JSON logs for machine processing

```python
from utilityhub_logging import LogFormat

log_file = configure_app_logging(
    app_name="myapp",
    log_format=LogFormat.JSON,
)
```

### Explicit logs directory

```python
log_file = configure_app_logging(
    app_name="myapp",
    logs_path="/tmp/myapp-logs",
)
```

### Configure propagation explicitly

```python
logger = logging.getLogger("myapp.api")

log_file = configure_app_logging(
    app_name="myapp",
    logger=logger,
    propagate=True,
)
```

Use `propagate=True` only if you intentionally want records to continue flowing to ancestor loggers.

## Clean Up Managed Handlers

```python
from utilityhub_logging import cleanup_logging

cleanup_logging(logger)
```

Call this during shutdown if you want to flush and close the managed handlers created by the package.

## What the Package Manages

- The file handlers it creates
- Optional console handlers it creates
- Duplicate-handler cleanup for repeated setup
- Bound session context like `app_name` and `session_id`

## What It Does Not Replace

`utilityhub_logging` extends stdlib `logging`; it does not replace it. You still use `logging.getLogger(...)`, standard log levels, and the normal logger methods.

[← Back to Guides](./index.md)
