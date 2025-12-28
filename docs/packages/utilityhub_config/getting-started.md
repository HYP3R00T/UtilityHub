---
icon: lucide/book-open
---

# Getting Started

## Installation

Install via pip:

```bash
pip install utilityhub_config
```

## Minimum Example

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    api_key: str
    timeout: int = 30

settings, metadata = load_settings(Config)
```

This will:
1. Use field defaults (if defined)
2. Check `~/.config/config/config.toml` and `~/.config/config/config.yaml`
3. Check `./config.toml` and `./config.yaml` in current directory
4. Check `.env` in current directory
5. Check environment variables (`API_KEY`, `TIMEOUT`)

## Working with Pydantic Models

Define your configuration as a Pydantic model with proper types and defaults:

```python
from pydantic import BaseModel, Field

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str

class AppConfig(BaseModel):
    app_name: str = "myapp"
    debug: bool = False
    database: DatabaseConfig
    max_workers: int = Field(default=4, gt=0)

settings, metadata = load_settings(AppConfig)
```

## Understanding Precedence

Settings are loaded in order, with each level overriding the previous:

```
Defaults (lowest priority)
    ↓
Global config (~/.config/...)
    ↓
Project config (./myapp.toml, etc.)
    ↓
.env file
    ↓
Environment variables
    ↓
Runtime overrides (highest priority)
```

Example showing precedence in action:

```python
# Model defines default
class Config(BaseModel):
    host: str = "localhost"

# Project config sets it to "0.0.0.0"
# Environment variable sets it to "192.168.1.1"
# Runtime override sets it to "custom.host"

settings, _ = load_settings(
    Config,
    overrides={"host": "custom.host"}
)

# Result: host = "custom.host" (overrides win)
```

## Configuring App Name

By default, the app name is derived from your model class name:

```python
class MyServiceConfig(BaseModel):
    debug: bool = False

# Looks for: ~/.config/myserviceconfig/myserviceconfig.toml
settings, _ = load_settings(MyServiceConfig)
```

Specify a custom app name:

```python
# Looks for: ~/.config/myapp/myapp.toml
settings, _ = load_settings(
    MyServiceConfig,
    app_name="myapp"
)
```

## Setting Config Directory

Specify where to search for config files:

```python
from pathlib import Path

settings, _ = load_settings(
    Config,
    app_name="myapp",
    cwd=Path("/etc/myapp")
)

# Looks for: /etc/myapp/myapp.toml, /etc/myapp/myapp.yaml
```

## Environment Variable Prefix

Avoid environment variable collisions with a prefix:

```python
# Without prefix: looks for API_KEY, TIMEOUT
settings, _ = load_settings(Config)

# With prefix: looks for MYAPP_API_KEY, MYAPP_TIMEOUT
settings, _ = load_settings(
    Config,
    env_prefix="MYAPP"
)
```

## Accessing Metadata

See where each setting came from:

```python
settings, metadata = load_settings(Config)

# Get source for a specific field
source = metadata.get_source("api_key")
if source:
    print(f"Source: {source.source}")        # "env", "project", etc.
    print(f"Path: {source.source_path}")     # File path or ENV variable name
    print(f"Value: {source.raw_value}")      # Original value before conversion

# Iterate all fields
for field_name, field_source in metadata.per_field.items():
    print(f"{field_name}: {field_source.source}")
```

## Handling Validation Errors

Use `try/except` for robust error handling:

```python
from utilityhub_config import load_settings
from utilityhub_config.errors import ConfigValidationError

try:
    settings, metadata = load_settings(Config)
except ConfigValidationError as e:
    # Error includes:
    # - Validation error details
    # - Files that were checked
    # - Precedence order
    # - Which sources provided which fields
    print(e)
    exit(1)
```

## Next Steps

- See [Examples](./examples.md) for common use cases
- Learn about [Configuration Files](./config-files.md) formats
- Check [Troubleshooting](./troubleshooting.md) for common issues
