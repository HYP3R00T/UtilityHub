# Getting Config Paths

## Overview

`get_config_path()` returns the canonical global configuration path for your application. This is useful when you want to know where `utilityhub_config` expects to find (or write) your application's global configuration file.

## Basic Usage

```python
from utilityhub_config import get_config_path

# Get the default TOML config path
toml_path = get_config_path("myapp")
print(toml_path)  # ~/.config/myapp/myapp.toml
```

## Supported Formats

The function supports three configuration formats:

```python
from utilityhub_config import get_config_path

# TOML (default)
toml_path = get_config_path("myapp")  # ~/.config/myapp/myapp.toml
toml_path = get_config_path("myapp", format="toml")  # Explicit

# YAML
yaml_path = get_config_path("myapp", format="yaml")  # ~/.config/myapp/myapp.yaml

# JSON
json_path = get_config_path("myapp", format="json")  # ~/.config/myapp/myapp.json
```

## Use Cases

### 1. Verify Config Location

Before loading settings, check where the config is expected to be:

```python
from utilityhub_config import get_config_path, load_settings
from pydantic import BaseModel

class Config(BaseModel):
    database_url: str = "sqlite:///default.db"

config_path = get_config_path("myapp")
print(f"Looking for config at: {config_path}")

settings, metadata = load_settings(Config, app_name="myapp")
```

### 2. Create Global Config Directory

Generate the config path to ensure the directory exists:

```python
from pathlib import Path
from utilityhub_config import get_config_path

config_path = get_config_path("myapp")
config_path.parent.mkdir(parents=True, exist_ok=True)
```

### 3. Bootstrap Configuration

Get the path where you plan to write a default config file:

```python
from utilityhub_config import get_config_path
from pydantic import BaseModel

class Config(BaseModel):
    database_url: str = "sqlite:///default.db"
    debug: bool = False

config_path = get_config_path("myapp")
# Later: write default config to this path (e.g., with write_config)
```

### 4. Choose Config Format

Dynamically determine which format to use:

```python
from utilityhub_config import get_config_path

# Use YAML if preferred
config_path = get_config_path("myapp", format="yaml")
print(f"Config format: {config_path.suffix}")  # .yaml
```

## Path Structure

The returned path follows a standard structure:

```
~/.config/{app_name}/{app_name}.{format}
```

Where:
- `~` is the user's home directory
- `.config` is the standard XDG Base Directory location
- `{app_name}` is the application name you provide
- `{format}` is the file extension (toml, yaml, or json)

### Examples

| Call | Result |
|------|--------|
| `get_config_path("myapp")` | `~/.config/myapp/myapp.toml` |
| `get_config_path("myapp", format="yaml")` | `~/.config/myapp/myapp.yaml` |
| `get_config_path("django")` | `~/.config/django/django.toml` |
| `get_config_path("web-server", format="json")` | `~/.config/web-server/web-server.json` |

## Integration with `load_settings`

`get_config_path()` returns the same path that `load_settings` uses internally when looking for global configuration:

```python
from utilityhub_config import get_config_path, load_settings
from pydantic import BaseModel

class Config(BaseModel):
    debug: bool = False

# These paths are identical:
canonical_path = get_config_path("myapp")

# When you call load_settings with app_name="myapp", it looks in this path
settings, metadata = load_settings(Config, app_name="myapp")
```

This consistency means:
- You can verify where `load_settings` will look
- You can prepare the directory before loading
- You have a canonical reference for the global config location

## Notes

- The path is **not validated for existence** — it may or may not exist on your system
- The function always returns an absolute path (starts with `/` on Linux/macOS, `C:\` on Windows)
- App names can include underscores, hyphens, dots, and numbers
- The function is cross-platform and works on Linux, macOS, and Windows

[← Back to Guides](./index.md)
