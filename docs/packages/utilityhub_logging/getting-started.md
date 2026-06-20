---
icon: lucide/rocket
---

# Getting Started

Install `utilityhub_logging` and configure one log file per application run.

## Installation

```bash
uv add utilityhub-logging
```

## Your First App Log

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

print(f"Writing logs to: {log_file}")
```

That call to `configure_app_logging()`:

1. Resolves a logs directory safely
2. Creates a timestamped log file for the current app session
3. Attaches managed handlers to the target logger
4. Optionally adds console output
5. Binds `app_name` and `session_id` into log context

## Add Context

```python
from utilityhub_logging import bind_context

with bind_context(environment="dev", subsystem="worker"):
    logger.info("Ready to process work")
```

This metadata will be included in the emitted log records.

## Create a Scoped Log

```python
from utilityhub_logging import begin_scope_logging, end_scope_logging

scope_logger, scope_file = begin_scope_logging(
    app_name="myapp",
    scope_type="job",
    scope_id="job-123",
)

scope_logger.info("Started scoped work")
end_scope_logging(scope_logger)
```

Use scoped logs when you want one file per operation, request, job, or task.

## Next Steps

👉 **Need the main patterns?** Read [Basic Usage](./guides/basic-usage.md)

👉 **Want every setup option explained?** Read [App Logging Configuration](./guides/app-logging-configuration.md)

👉 **Want to control directories?** See [Log Paths](./guides/log-paths.md)

👉 **Need structured output?** Read [Structured Logging](./guides/structured-logging.md)

👉 **Using context heavily?** See [Context Binding](./guides/context-binding.md)

👉 **Need realistic setups?** Read [Examples](./examples.md)
