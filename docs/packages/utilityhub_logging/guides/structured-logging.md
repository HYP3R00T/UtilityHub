# Structured Logging

`utilityhub_logging` supports two output formats:

- plain text for humans
- JSON for machines and downstream processing

## Plain Text

```python
from utilityhub_logging import LogFormat, configure_app_logging

configure_app_logging(
    app_name="myapp",
    log_format=LogFormat.PLAIN,
)
```

Plain text output is designed for easy reading in local development and terminal sessions.

## JSON

```python
from utilityhub_logging import LogFormat, configure_app_logging

configure_app_logging(
    app_name="myapp",
    log_format=LogFormat.JSON,
)
```

JSON output is useful for ingestion by log processors and aggregation systems.

Example JSON record shape:

```json
{
  "context": {
    "app_name": "myapp",
    "session_id": "abcd1234",
    "user_id": "u-42"
  },
  "level": "INFO",
  "logger": "myapp",
  "message": "Processing started",
  "timestamp": "2026-06-20T12:00:00.000Z"
}
```

## Format Selection

You can use the same format choice for both app-session logging and scoped logging.

[← Back to Guides](./index.md)
