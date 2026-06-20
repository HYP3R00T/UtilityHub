# App Logging Configuration

This guide explains what you can configure when calling `configure_app_logging()`.

## Signature

```python
configure_app_logging(
    app_name: str,
    *,
    level: int | str = "INFO",
    logs_path: str | Path | None = None,
    default_convention: LogPathConvention | str = LogPathConvention.PLATFORM,
    console: bool = True,
    log_format: LogFormat | str = LogFormat.PLAIN,
    logger: logging.Logger | None = None,
    propagate: bool = False,
) -> Path
```

## What It Returns

It returns the `Path` to the session log file created for that application run.

## Parameters

### `app_name`

```python
configure_app_logging(app_name="myapp")
```

This is the only required argument.

It is used to:

- determine the default logs directory when `logs_path` is not provided
- generate the session log filename
- bind `app_name` into the logging context

### `level`

```python
configure_app_logging(app_name="myapp", level="DEBUG")
configure_app_logging(app_name="myapp", level=logging.WARNING)
```

Controls the logger level and the managed handler levels created by the package.

You can pass either:

- a string such as `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`
- an integer logging level such as `logging.INFO`

### `logs_path`

```python
configure_app_logging(app_name="myapp", logs_path="/tmp/myapp-logs")
```

Use this when you want complete control over where log files are stored.

If provided, it overrides the default path convention.

### `default_convention`

```python
from utilityhub_logging import LogPathConvention

configure_app_logging(
    app_name="myapp",
    default_convention=LogPathConvention.HOME_HIDDEN,
)
```

Used only when `logs_path` is omitted.

Available values:

- `LogPathConvention.PLATFORM`
- `LogPathConvention.HOME_HIDDEN`
- `LogPathConvention.CWD`

`PLATFORM` is the default and is the safest general-purpose choice.

### `console`

```python
configure_app_logging(app_name="myapp", console=False)
```

Controls whether a managed `StreamHandler` is added in addition to the file handler.

- `True`: logs go to the session file and console
- `False`: logs go only to the session file created by this package

### `log_format`

```python
from utilityhub_logging import LogFormat

configure_app_logging(app_name="myapp", log_format=LogFormat.PLAIN)
configure_app_logging(app_name="myapp", log_format=LogFormat.JSON)
```

Selects how records are formatted.

- `LogFormat.PLAIN` for human-readable output
- `LogFormat.JSON` for machine-readable structured output

### `logger`

```python
logger = logging.getLogger("myapp.worker")

configure_app_logging(app_name="myapp", logger=logger)
```

By default, `configure_app_logging()` configures the root logger.

Pass a specific logger when you want logging setup isolated to part of your application.

### `propagate`

```python
logger = logging.getLogger("myapp.worker")

configure_app_logging(
    app_name="myapp",
    logger=logger,
    propagate=True,
)
```

Controls whether log records continue propagating to ancestor loggers.

- `False`: records stop at the configured logger
- `True`: records can also be handled by parent loggers

For most setups, `False` avoids surprising duplicate output.

## Behavior Notes

When you call `configure_app_logging()` the package also:

- removes managed app handlers it previously created on that logger
- creates a timestamped UTF-8 log file
- binds `app_name` and `session_id` into the logging context

## Example Configurations

### Minimal setup

```python
configure_app_logging(app_name="myapp")
```

### Verbose local development

```python
configure_app_logging(
    app_name="myapp",
    level="DEBUG",
    console=True,
    log_format="plain",
)
```

### Structured worker logging

```python
configure_app_logging(
    app_name="myapp",
    level="INFO",
    console=False,
    log_format="json",
    logs_path="/var/tmp/myapp-logs",
)
```

### Configure a non-root logger

```python
logger = logging.getLogger("myapp.jobs")

configure_app_logging(
    app_name="myapp",
    logger=logger,
    level="DEBUG",
    propagate=False,
)
```

[← Back to Guides](./index.md)
