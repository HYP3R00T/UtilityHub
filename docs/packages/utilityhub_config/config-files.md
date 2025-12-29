---
icon: lucide/code
---

# Configuration Files

## Supported Formats

`utilityhub_config` supports three configuration file formats:

- **TOML** - `.toml` files (recommended for clarity)
- **YAML** - `.yaml` or `.yml` files
- **.env** - `.env` files with `KEY=VALUE` pairs

## TOML Format

Most readable and recommended format.

```toml
# ~/.config/myapp/myapp.toml
app_name = "myapp"
debug = false
max_workers = 8

[database]
host = "localhost"
port = 5432
username = "app_user"
password = "secret"
```

Usage:

```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str

class AppConfig(BaseModel):
    app_name: str
    debug: bool
    max_workers: int
    database: DatabaseConfig

settings, _ = load_settings(AppConfig, app_name="myapp")
# Loads from ~/.config/myapp/myapp.toml
```

## YAML Format

Hierarchical configuration with YAML syntax.

```yaml
# ~/.config/myapp/myapp.yaml
app_name: myapp
debug: false
max_workers: 8

database:
  host: localhost
  port: 5432
  username: app_user
  password: secret
```

Usage is identical to TOML:

```python
settings, _ = load_settings(AppConfig, app_name="myapp")
# Loads from ~/.config/myapp/myapp.yaml
```

## .env Format

Simple key-value format, commonly used with environment variables.

```env
# .env (in current working directory)
DEBUG=false
MAX_WORKERS=8
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=app_user
DATABASE_PASSWORD=secret
```

## File Search Locations

`load_settings()` searches for configuration in this order:

### Global Config

Located in user's home directory:

```
~/.config/{app_name}/{app_name}.toml
~/.config/{app_name}/{app_name}.yaml
```

### Project Config

Located in working directory:

```
{cwd}/{app_name}.toml
{cwd}/{app_name}.yaml
{cwd}/config/{app_name}.toml
{cwd}/config/{app_name}.yaml
{cwd}/config/*.toml
{cwd}/config/*.yaml
```

### .env File

```
{cwd}/.env
```

## Complete Example

Combining all three formats in a single hierarchy:

**~/.config/myapp/myapp.toml** (Global defaults):
```toml
app_name = "myapp"
log_level = "INFO"
database.host = "prod.example.com"
database.port = 5432
```

**./myapp.yaml** (Project-specific):
```yaml
log_level: DEBUG
max_workers: 8
```

**.env** (Local machine overrides):
```env
DATABASE_PASSWORD=local_dev_password
API_KEY=dev_key_12345
```

Result after precedence resolution:

```python
settings, metadata = load_settings(AppConfig)

settings.app_name        # "myapp" (from global)
settings.log_level       # "DEBUG" (from project, overrides global)
settings.max_workers     # 8 (from project)
settings.database.host   # "prod.example.com" (from global)
settings.database.port   # 5432 (from global)

# If PASSWORD env var exists, it will be used
# Otherwise, uses .env or model defaults
```

## Type Conversion

All file values are converted to match your Pydantic model types:

```toml
# myapp.toml
port = 8080
debug = true
workers = 4
timeout = 30.5
tags = ["api", "web"]
```

```python
class Config(BaseModel):
    port: int           # "8080" converted to int
    debug: bool         # "true" converted to bool
    workers: int        # 4 as int
    timeout: float      # 30.5 as float
    tags: list[str]     # Array as list

settings, _ = load_settings(Config)
# All values properly typed
```

## Nested Configuration

Define nested structures in your files:

**TOML:**
```toml
[database]
host = "localhost"
port = 5432
username = "user"

[cache]
enabled = true
ttl = 3600
```

**YAML:**
```yaml
database:
  host: localhost
  port: 5432
  username: user

cache:
  enabled: true
  ttl: 3600
```

**Python:**
```python
class DatabaseConfig(BaseModel):
    host: str
    port: int
    username: str

class CacheConfig(BaseModel):
    enabled: bool
    ttl: int

class AppConfig(BaseModel):
    database: DatabaseConfig
    cache: CacheConfig

settings, _ = load_settings(AppConfig)
```

## Comments and Readability

**TOML** supports inline comments:

```toml
# Global settings
app_name = "myapp"
debug = false  # Disabled in production

# Database configuration
[database]
host = "localhost"  # Connect to local database
port = 5432         # PostgreSQL default port
```

**YAML** also supports comments:

```yaml
# Global settings
app_name: myapp
debug: false  # Disabled in production

# Database configuration
database:
  host: localhost  # Connect to local database
  port: 5432       # PostgreSQL default port
```

## Best Practices

1. **Use TOML** - Most readable, structured format
2. **Keep secrets out** - Use environment variables for sensitive data
3. **Version control** - Commit config templates, not real values
4. **Use .gitignore** - Exclude `.env` and local config files
5. **Document defaults** - Make model defaults clear with docstrings

Example `.gitignore`:

```
.env
.env.local
*.local.toml
*.local.yaml
```
