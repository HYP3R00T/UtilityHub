---
icon: lucide/settings
---

# utilityhub_logging

A **project-agnostic logging helper package** built on top of Python's standard library `logging` module. It helps applications create predictable log files, attach structured context, manage scoped logs, and clean up handlers safely.

## Why This Package Exists

Python's built-in `logging` module is flexible, but teams still end up writing the same orchestration code around it.

That usually includes:

- deciding where logs should live
- creating one file per application run
- opening dedicated logs for individual operations
- choosing between human-readable and structured output
- attaching context like session IDs or request IDs
- preventing duplicate handlers during repeated setup
- shutting handlers down cleanly

`utilityhub_logging` exists to provide that reusable orchestration layer without replacing stdlib logging.

## What Problem It Solves

As applications get larger, logging setup often becomes inconsistent across scripts, workers, services, and background jobs.

Common pain points include:

- log files ending up in inconsistent or unsafe locations
- repeated handler setup creating duplicate output
- no standard way to create one log per app run
- no reusable pattern for one log per request, job, or task
- context fields being added inconsistently across the codebase
- file handlers being left open longer than expected

`utilityhub_logging` solves this by standardizing setup, context, scoping, and cleanup while keeping the familiar stdlib logger model.

## What It Does

`utilityhub_logging` handles the setup and lifecycle pieces teams usually reimplement around stdlib logging:

- ✅ **Safe log path resolution** - Resolve a platform-aware logs directory or use an explicit path
- ✅ **One log per app run** - Create a timestamped app-session log file
- ✅ **Scoped logs** - Open a dedicated log file for a request, job, task, or other operation
- ✅ **Plain text or JSON** - Switch between human-readable and machine-readable output
- ✅ **Context binding** - Attach metadata like `app_name`, `session_id`, `request_id`, or `job_id`
- ✅ **Handler lifecycle management** - Prevent duplicate handlers and close managed handlers cleanly

## Feature Highlights

- **App-session logging** with `configure_app_logging()`
- **Scoped operation logging** with `begin_scope_logging()` and `end_scope_logging()`
- **Safe logs directory resolution** with `resolve_logs_path()`
- **Structured context binding** with `bind_context()`
- **Plain text and JSON output modes**
- **Managed handler cleanup** with `cleanup_logging()`
- **Project-agnostic design** that works across CLIs, workers, services, and libraries

## Quick Start

```bash
uv add utilityhub-logging
```

```python
import logging

from utilityhub_logging import configure_app_logging

log_file = configure_app_logging(
    app_name="demo-app",
    level="INFO",
    console=True,
)

logger = logging.getLogger("demo")
logger.info("Application started")

print(log_file)
```

## Documentation

### Getting Started
- [Installation & Quick Start](./getting-started.md) - Set up app logging in a few minutes

### Usage Guides
- [Guide Index](./guides/index.md) - Browse the available guides
- [Basic Usage](./guides/basic-usage.md) - Configure application logging and write messages
- [Log Paths](./guides/log-paths.md) - Understand path resolution and safe defaults
- [Scoped Logging](./guides/scoped-logging.md) - Create a dedicated log for an operation
- [Structured Logging](./guides/structured-logging.md) - Switch between plain text and JSON output
- [Context Binding](./guides/context-binding.md) - Attach metadata consistently to log records

### Examples
- [Examples](./examples.md) - Realistic logging setups for CLIs, workers, services, and subsystems

### Help
- [Guide Index](./guides/index.md) - Browse all logging guides

## Public API At a Glance

```python
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
```

## Where to Go Next

👉 **New here?** Start with [Getting Started](./getting-started.md)

👉 **Need the common setup?** Read [Basic Usage](./guides/basic-usage.md)

👉 **Want realistic setups?** Read [Examples](./examples.md)

👉 **Want per-operation logs?** Jump to [Scoped Logging](./guides/scoped-logging.md)

👉 **Need JSON output?** See [Structured Logging](./guides/structured-logging.md)
