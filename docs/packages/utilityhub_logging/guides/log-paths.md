# Log Paths

## Resolve a Logs Directory

```python
from utilityhub_logging import resolve_logs_path

logs_dir = resolve_logs_path("myapp")
print(logs_dir)
```

By default, `utilityhub_logging` avoids writing into the current working directory unless you explicitly request that convention.

## Default Conventions

Platform-aware defaults are used when `logs_path` is not provided:

- Linux and similar Unix systems: `~/.local/state/<app>/logs`
- macOS: `~/Library/Logs/<app>`
- Windows: `%LOCALAPPDATA%\<app>\Logs`

## Use an Explicit Path

```python
logs_dir = resolve_logs_path(
    "myapp",
    logs_path="/var/log/myapp",
)
```

The directory will be created if needed.

## Use a Different Convention

```python
from utilityhub_logging import LogPathConvention, resolve_logs_path

logs_dir = resolve_logs_path(
    "myapp",
    default_convention=LogPathConvention.HOME_HIDDEN,
)
```

Available conventions:

- `LogPathConvention.PLATFORM`
- `LogPathConvention.HOME_HIDDEN`
- `LogPathConvention.CWD`

Use `CWD` only when writing logs under the current working directory is intentional.

[← Back to Guides](./index.md)
