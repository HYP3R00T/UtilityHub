# Path Expansion

utilityhub_config provides utilities to automatically expand paths with tilde (`~`) and environment variables in your configuration files. This is especially useful for cross-platform applications where paths should be resolved at runtime.

## Overview

Path expansion supports:

- **Tilde expansion** (`~`): Expands to the user's home directory
  - `~/config/app.yaml` → `/home/username/config/app.yaml`
- **Environment variables** (`$VAR` or `${VAR}`): Expands environment variable references
  - `$HOME/config` → `/home/username/config`
  - `${CONFIG_DIR}/app.yaml` → `/etc/myapp/app.yaml`
- **Path validation**: Optionally validate that paths exist after expansion

## Utility Functions

### `expand_path(path: str) -> Path`

Expand a path string without validation.

```python
from utilityhub_config import expand_path

# Tilde expansion
expanded = expand_path("~/config/app.yaml")
print(expanded)  # PosixPath('/home/username/config/app.yaml')

# Environment variable expansion
expanded = expand_path("$CONFIG_DIR/app.yaml")
print(expanded)  # PosixPath('/etc/myapp/app.yaml')

# Combined expansion
expanded = expand_path("~/$APP_NAME/config.toml")
```

### `expand_and_validate_path(path: str) -> Path`

Expand a path and validate that it exists.

```python
from utilityhub_config import expand_and_validate_path

# Raises FileNotFoundError if path doesn't exist
config_path = expand_and_validate_path("~/config/app.yaml")
print(config_path)  # PosixPath('/home/username/config/app.yaml')
```

## Using with Pydantic Models

For automatic path expansion in your configuration models, use the `expand_path_validator` function with Pydantic's field validator decorator:

### Example: Basic Path Field

```python
from pathlib import Path
from pydantic import BaseModel, field_validator
from utilityhub_config import load_settings, expand_path_validator

class Config(BaseModel):
    config_file: Path
    log_dir: Path

    @field_validator("config_file", "log_dir", mode="before")
    @classmethod
    def expand_paths(cls, v: Path | str) -> Path:
        return expand_path_validator(v)

# Load configuration
settings, _ = load_settings(Config, app_name="myapp")
```

### Configuration File with Expanded Paths

`myapp.toml`:
```toml
config_file = "~/.config/myapp/app.toml"
log_dir = "$LOG_ROOT/myapp"
```

At runtime, these will be expanded to absolute paths.

## Cross-Platform Usage

Path expansion works consistently across platforms:

**Unix/Linux/macOS:**
```
~ → /home/username
$HOME → /home/username
```

**Windows:**
```
~ → C:\Users\username
%USERPROFILE% → C:\Users\username
```

Environment variable expansion uses the system's native conventions.

## Examples

### Example 1: Database Configuration

```python
from pathlib import Path
from pydantic import BaseModel, field_validator
from utilityhub_config import load_settings, expand_path_validator

class DatabaseConfig(BaseModel):
    db_file: Path
    backup_dir: Path

    @field_validator("db_file", "backup_dir", mode="before")
    @classmethod
    def expand_db_paths(cls, v: Path | str) -> Path:
        return expand_path_validator(v)

# config.yaml:
# db_file: ~/myapp/data.db
# backup_dir: $BACKUP_ROOT/myapp

settings, _ = load_settings(DatabaseConfig, app_name="myapp")
print(settings.db_file)      # /home/user/myapp/data.db
print(settings.backup_dir)   # /var/backups/myapp
```

### Example 2: Logging Configuration

```python
from pathlib import Path
from pydantic import BaseModel, field_validator
from utilityhub_config import load_settings, expand_path_validator

class LogConfig(BaseModel):
    log_file: Path
    error_log: Path

    @field_validator("log_file", "error_log", mode="before")
    @classmethod
    def expand_log_paths(cls, v: Path | str) -> Path:
        return expand_path_validator(v)

# .env:
# LOG_FILE=~/logs/app.log
# ERROR_LOG=$LOG_DIR/errors.log

settings, _ = load_settings(LogConfig)
```

### Example 3: Mixed Configuration Sources

```python
from pathlib import Path
from pydantic import BaseModel, field_validator
from utilityhub_config import load_settings, expand_path_validator

class AppConfig(BaseModel):
    config_dir: Path
    data_dir: Path
    credentials_file: Path

    @field_validator("config_dir", "data_dir", "credentials_file", mode="before")
    @classmethod
    def expand_all_paths(cls, v: Path | str) -> Path:
        return expand_path_validator(v)

# Priority order (from lowest to highest):
# 1. app.yaml: data_dir = ~/data
# 2. Environment: DATA_DIR=/var/lib/myapp
# 3. Runtime override: credentials_file=/secure/creds.json

settings, meta = load_settings(
    AppConfig,
    app_name="myapp",
    overrides={"credentials_file": "/secure/creds.json"}
)
```

## Error Handling

When a path doesn't exist after expansion, a `FileNotFoundError` is raised:

```python
from utilityhub_config import expand_and_validate_path
from pathlib import Path
from pydantic import BaseModel, field_validator, ValidationError
from utilityhub_config import load_settings, expand_path_validator

class Config(BaseModel):
    config_file: Path

    @field_validator("config_file", mode="before")
    @classmethod
    def expand_config(cls, v: Path | str) -> Path:
        return expand_path_validator(v)

try:
    # This will fail if ~/nonexistent.yaml doesn't exist
    settings, _ = load_settings(
        Config,
        overrides={"config_file": "~/nonexistent.yaml"}
    )
except ValidationError as e:
    print(f"Configuration error: {e}")
```

## Tips & Best Practices

### 1. Validate Paths in Development

Always test your path configurations to ensure they resolve correctly:

```python
from utilityhub_config import expand_path

config_path = expand_path("~/myapp/config.yaml")
print(f"Config will be loaded from: {config_path}")
```

### 2. Use Environment Variables for Flexibility

Instead of hardcoding paths, use environment variables:

```toml
# config.toml (good)
data_dir = "$DATA_ROOT/myapp"

# config.toml (avoid)
data_dir = "/var/lib/myapp"
```

### 3. Set Environment Variables in Startup Scripts

Ensure environment variables are available where your application runs:

```bash
#!/bin/bash
export LOG_ROOT="/var/log"
export DATA_ROOT="/var/lib"
python -m myapp
```

### 4. Document Path Expectations

In your application's README or configuration guide, document what paths are used:

```markdown
## Configuration

- `config_file`: Primary configuration file (required)
- `log_dir`: Directory for application logs
- `data_dir`: Directory for application data storage

Supports tilde (`~`) and environment variables.
```

[← Back to Guides](./index.md)
