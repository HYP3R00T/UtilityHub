# Context Binding

Context binding lets you attach metadata to log records without manually repeating it in every message.

## Bind Context

```python
from utilityhub_logging import bind_context

with bind_context(request_id="req-123", user_id="u-42"):
    logger.info("Handling request")
```

## Common Metadata

Typical keys include:

- `app_name`
- `session_id`
- `request_id`
- `user_id`
- `job_id`
- `environment`
- `subsystem`

The package already binds `app_name` and `session_id` when app logging is configured. Scoped logging also binds `scope_type` and `scope_id`.

## Why Use It

Context binding helps you:

- correlate related log events
- filter logs more effectively
- avoid repeating IDs in every message string
- keep metadata available in both plain text and JSON output

## Async-Safe Design

The package uses `contextvars`, which makes context binding safe for concurrent and async-heavy applications.

[← Back to Guides](./index.md)
