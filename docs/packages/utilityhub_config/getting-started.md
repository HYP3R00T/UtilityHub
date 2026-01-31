---
icon: lucide/rocket
---

# Getting Started

Install and run your first configuration loader in 5 minutes.

## Installation

```bash
pip install utilityhub_config
```

Optional dependencies:

```bash
# For YAML support
pip install pyyaml

# For .env file support
pip install python-dotenv
```

## Your First Config

Create a simple configuration:

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    database_url: str = "sqlite:///default.db"
    debug: bool = False
    workers: int = 4

# Load settings from all available sources
settings, metadata = load_settings(Config)

# Use your settings
print(f"Database: {settings.database_url}")
print(f"Debug mode: {settings.debug}")
print(f"Workers: {settings.workers}")
```

That's it! `load_settings()` automatically:

1. Uses model field defaults
2. Checks `~/.config/config/config.toml` and `.yaml`
3. Checks `./config.toml` and `./config.yaml` in current directory
4. Reads `.env` in current directory
5. Checks environment variables (`DATABASE_URL`, `DEBUG`, `WORKERS`)

## See Where Values Come From

```python
settings, metadata = load_settings(Config)

# Check the source of a field
source = metadata.get_source("database_url")
print(f"Came from: {source.source}")        # "env", "project", "defaults", etc.
print(f"File: {source.source_path}")        # Full path or "ENV:DATABASE_URL"
print(f"Raw value: {source.raw_value}")     # Original value before validation
```

## Next Steps

Choose your path:

👉 **Want to understand precedence?** Read [Precedence Order](./concepts/precedence.md)

👉 **Ready to use files?** Jump to [Configuration Files guide](./guides/configuration-files.md)

👉 **Using environment?** See [Environment Variables guide](./guides/environment-variables.md)

👉 **Need specific patterns?** Browse [Usage Guides](./guides/index.md)

👉 **Troubleshooting?** Check [Troubleshooting guide](./troubleshooting.md)

## Common Tasks

### Use a Config File

```python
from pathlib import Path

settings, _ = load_settings(
    Config,
    config_file=Path("./production.yaml")
)
```

See [Explicit Config Files guide](./guides/explicit-config-files.md)

### Use Environment Variable Prefix

```python
settings, _ = load_settings(
    Config,
    env_prefix="MYAPP"  # Looks for MYAPP_DATABASE_URL, etc.
)
```

See [Environment Variables guide](./guides/environment-variables.md)

### Override at Runtime

```python
settings, _ = load_settings(
    Config,
    overrides={
        "debug": True,
        "workers": 8
    }
)
```

See [Runtime Overrides guide](./guides/runtime-overrides.md)

### Handle Errors

```python
from utilityhub_config.errors import ConfigValidationError

try:
    settings, _ = load_settings(Config)
except ConfigValidationError as e:
    print(f"Configuration error: {e}")
```

See [Error Handling guide](./guides/error-handling.md)

## What's Different?

`utilityhub_config` is **explicit, not magical**:

- ✅ Precedence is **clear and documented**
- ✅ You know **exactly where** each setting came from (metadata)
- ✅ **Type safety** via Pydantic
- ✅ **No hidden behavior** — what you see is what you get
- ✅ **Rich errors** when validation fails

## Learn More

- [Complete Guide Index](./guides/index.md)
- [Core Concepts](./concepts/index.md)
- [FAQ & Troubleshooting](./troubleshooting.md)
