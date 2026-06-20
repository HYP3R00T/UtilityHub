# Scoped Logging

Scoped logging creates a dedicated log file for an operation such as a request, job, batch, import, or task.

## Start a Scope

```python
from utilityhub_logging import begin_scope_logging

scope_logger, scope_file = begin_scope_logging(
    app_name="myapp",
    scope_type="job",
    scope_id="job-123",
    level="DEBUG",
)

scope_logger.info("Scope started")
print(scope_file)
```

This creates a file under a scoped directory like:

```text
<logs_root>/scopes/job/job-123-<timestamp>.log
```

## End a Scope

```python
from utilityhub_logging import end_scope_logging

end_scope_logging(scope_logger)
```

That removes, flushes, and closes the managed scope handlers for that logger.

## When to Use It

Scoped logging is useful when you want one file per unit of work:

- web requests
- background jobs
- queued tasks
- imports and exports
- batch runs

## Relationship to App Logging

Scoped logging does not replace app logging. A common pattern is:

1. Configure app logging once at process startup
2. Start a scoped log when a request or job begins
3. End the scoped log when that unit of work finishes

[← Back to Guides](./index.md)
