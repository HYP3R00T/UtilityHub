# Getting Config Paths

## Overview

`utilityhub_config` provides three utility functions for working with configuration file paths and content:

- **`get_config_path()`** - Get the canonical global configuration path for your application
- **`write_config()`** - Serialize a model instance and write it to the config file location
- **`ensure_config_file()`** - Ensure a config file exists, creating it from model defaults if needed

These functions work together to provide a complete toolkit for managing application configuration files.

## Basic Usage

```python
from utilityhub_config import get_config_path

# Get the default TOML config path
toml_path = get_config_path("myapp")
print(toml_path)  # ~/.config/myapp/myapp.toml
```

## Supported Formats

The function supports two configuration formats:

```python
from utilityhub_config import get_config_path

# TOML (default)
toml_path = get_config_path("myapp")  # ~/.config/myapp/myapp.toml
toml_path = get_config_path("myapp", format="toml")  # Explicit

# YAML
yaml_path = get_config_path("myapp", format="yaml")  # ~/.config/myapp/myapp.yaml
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
- `{format}` is the file extension (toml or yaml)

### Examples

| Call | Result |
|------|--------|
| `get_config_path("myapp")` | `~/.config/myapp/myapp.toml` |
| `get_config_path("myapp", format="yaml")` | `~/.config/myapp/myapp.yaml` |
| `get_config_path("django")` | `~/.config/django/django.toml` |

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

- The path is **not validated for existence** - it may or may not exist on your system
- The function always returns an absolute path (starts with `/` on Linux/macOS, `C:\` on Windows)
- App names can include underscores, hyphens, dots, and numbers

## Writing Configuration Files

### `write_config()`

The `write_config()` function serializes a Pydantic model instance and writes it to disk. By default it writes to the standard global config location for your application.

```python
from pydantic import BaseModel
from utilityhub_config import write_config

class Config(BaseModel):
    database_url: str = "sqlite:///app.db"
    debug: bool = False

config = Config(debug=True)

write_config(config, "myapp")
```

#### Parameters

- **`instance`** *(BaseModel)*: The Pydantic model instance to serialize and write.
- **`app_name`** *(str)*: Your application name (used to determine config location)
- **`path`** *(Path, optional)*: Explicit output file path. If provided, this path is used instead of the canonical global path.
- **`format`** *(str, optional)*: The file format to use. Options: `"toml"`, `"yaml"`. If not specified, defaults to `"toml"`.

#### Behavior

- Creates the config directory if it doesn't exist
- Writes the serialized model data in the specified format
- Uses the standard global config path when `path` is not provided
- Overwrites existing files without warning

#### Use Cases

- **Initial Setup**: Create default configuration files during application installation
- **Configuration Export**: Save current runtime configuration to disk
- **Backup**: Create backups of configuration state
- **Migration**: Write updated configuration after format changes

### `ensure_config_file()`

The `ensure_config_file()` function ensures a configuration file exists, creating it from a Pydantic model instance if it doesn't exist. If the file already exists, it leaves it unchanged.

```python
from pydantic import BaseModel
from utilityhub_config import ensure_config_file

class Config(BaseModel):
    api_url: str = "https://api.example.com"
    timeout: int = 30

defaults = Config()

config_path = ensure_config_file(defaults, "myapp")
print(f"Config file ready at: {config_path}")
```

#### Parameters

- **`instance`** *(BaseModel)*: The Pydantic model instance to serialize if the file does not exist.
- **`app_name`** *(str)*: Your application name (used to determine config location)
- **`path`** *(Path, optional)*: Explicit output file path. If provided, this path is used instead of the canonical global path.
- **`format`** *(str, optional)*: The file format to use. Options: `"toml"`, `"yaml"`. If not specified, defaults to `"toml"`.

#### Returns

- **Path**: The path to the configuration file (whether it was created or already existed)

#### Behavior

- Checks if config file exists at standard location
- If file exists: returns the path without modification
- If file doesn't exist: creates directory structure and writes serialized model defaults
- Never overwrites existing configuration files

#### Use Cases

- **First Run Setup**: Ensure configuration exists on application startup
- **Safe Defaults**: Provide fallback configuration without overwriting user changes
- **Installation Scripts**: Set up initial configuration during deployment
- **Development**: Create local config files with development defaults
- The function is cross-platform and works on Linux, macOS, and Windows

[← Back to Guides](./index.md)
