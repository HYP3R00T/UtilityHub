# Basic Usage

## Install

```bash
uv add utilityhub_config
```

## Your First Config

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    database_url: str = "sqlite:///default.db"
    debug: bool = False
    workers: int = 4

settings, metadata = load_settings(Config)
print(settings.database_url)  # Uses defaults or loaded values
```

## Config Lookup Paths

`load_settings()` resolves config values from multiple sources; in the global and project config steps it uses a derived app name.

- If `app_name` is provided, it is used directly.
- If `app_name` is omitted:
  1. If model has `app_name` field with default, that value is used.
  2. Otherwise, fallback is `model.__name__.lower()`.

### Example: explicit `app_name`

```python
settings, _ = load_settings(Config, app_name="myapp")
# Global config lookup order (both are checked but neither is auto-created):
#   1) ~/.config/myapp/myapp.toml
#   2) ~/.config/myapp/myapp.yaml
# If both exist, YAML values override TOML.
# Project config lookup (cwd):
#   1) ./myapp.toml
#   2) ./myapp.yaml
# Project config lookup (config/ dir):
#   ./config/*.toml, ./config/*.yaml, ./config/*.yml
```

### Example: omitted `app_name` (fallback to class name)

```python
settings, _ = load_settings(Config)
# Global config:
#   ~/.config/config/config.toml
#   ~/.config/config/config.yaml
# Project config (cwd):
#   ./config.toml
#   ./config.yaml
```

## Check Sources

```python
settings, metadata = load_settings(Config)
source = metadata.get_source("database_url")
print(f"{source.source}: {source.source_path}")
```

[← Back to Guides](./index.md)
