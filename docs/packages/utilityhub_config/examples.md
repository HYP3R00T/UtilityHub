---
icon: lucide/lightbulb
---

# Examples

## Basic Usage

### Minimal Setup

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    api_key: str
    timeout: int = 30

settings, _ = load_settings(Config)
print(settings.api_key)
print(settings.timeout)
```

### With Default Values

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    workers: int = 4

settings, _ = load_settings(Config)
# Uses defaults if not provided in config files or environment
```

## Tracking Configuration Sources

### See Where Each Setting Came From

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    database_url: str = "sqlite:///default.db"
    api_key: str = "default_key"
    debug: bool = False

settings, metadata = load_settings(Config)

# Check each setting's source
for field_name, field_source in metadata.per_field.items():
    print(f"{field_name}:")
    print(f"  Source: {field_source.source}")        # defaults, env, project, etc.
    print(f"  Path: {field_source.source_path}")     # File path or ENV:VAR_NAME
    print(f"  Raw value: {field_source.raw_value}")  # Original value
    print()
```

### Get Source for Specific Field

```python
settings, metadata = load_settings(Config)

db_source = metadata.get_source("database_url")
if db_source:
    print(f"Database URL came from: {db_source.source}")
    if db_source.source == "env":
        print(f"Environment variable: {db_source.source_path}")
    else:
        print(f"File: {db_source.source_path}")
```

## Environment Variables

### Basic Environment Variable Usage

```python
import os
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    api_key: str
    debug: bool = False

# Set environment variables
os.environ["API_KEY"] = "secret123"
os.environ["DEBUG"] = "true"

settings, _ = load_settings(Config)
print(settings.api_key)   # "secret123"
print(settings.debug)     # True
```

### Using Environment Variable Prefix

```python
import os
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    database_url: str
    api_key: str
    port: int = 8080

# Set prefixed environment variables
os.environ["MYAPP_DATABASE_URL"] = "postgresql://localhost/mydb"
os.environ["MYAPP_API_KEY"] = "secret"
os.environ["MYAPP_PORT"] = "3000"

settings, _ = load_settings(
    Config,
    env_prefix="MYAPP"
)

print(settings.database_url)  # "postgresql://localhost/mydb"
print(settings.api_key)       # "secret"
print(settings.port)          # 3000
```

## Runtime Overrides

### Override Everything at Runtime

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    app_name: str = "default"
    debug: bool = False
    workers: int = 4

# Runtime overrides take highest priority
settings, _ = load_settings(
    Config,
    overrides={
        "app_name": "production",
        "debug": False,
        "workers": 16
    }
)

print(settings.app_name)   # "production"
print(settings.workers)    # 16
```

### Conditional Overrides

```python
import os
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    debug: bool = False
    log_level: str = "INFO"
    max_retries: int = 3

# Override based on environment
overrides = {}
if os.getenv("CI"):
    overrides["debug"] = False
    overrides["log_level"] = "WARNING"
    overrides["max_retries"] = 5

settings, _ = load_settings(Config, overrides=overrides)
```

## Nested Configuration

### Nested Models

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str

class CacheConfig(BaseModel):
    enabled: bool = True
    ttl: int = 3600

class AppConfig(BaseModel):
    app_name: str = "myapp"
    debug: bool = False
    database: DatabaseConfig
    cache: CacheConfig

settings, _ = load_settings(AppConfig)
print(settings.database.host)
print(settings.cache.ttl)
```

## Error Handling

### Graceful Error Handling

```python
from pydantic import BaseModel
from utilityhub_config import load_settings
from utilityhub_config.errors import ConfigValidationError

class Config(BaseModel):
    port: int
    api_key: str

try:
    settings, metadata = load_settings(Config)
except ConfigValidationError as e:
    print(f"Configuration error: {e.message}")
    print(f"\nValidation errors:")
    print(e.errors)
    print(f"\nFiles checked:")
    for file in e.checked_files:
        print(f"  - {file}")
    print(f"\nPrecedence order:")
    print(f"  {' > '.join(e.precedence)}")
    exit(1)
```

### Log Configuration Loading

```python
import logging
from pydantic import BaseModel
from utilityhub_config import load_settings

logger = logging.getLogger(__name__)

class Config(BaseModel):
    app_name: str = "myapp"
    debug: bool = False

try:
    settings, metadata = load_settings(Config)

    logger.info("Configuration loaded successfully")
    logger.debug("Configuration sources:")
    for field, source in metadata.per_field.items():
        logger.debug(f"  {field}: {source.source} ({source.source_path})")

except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise
```

## Custom App Names and Directories

### Using Custom App Name

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class ServiceConfig(BaseModel):
    host: str = "localhost"
    port: int = 8080

# Uses ~/.config/myservice/myservice.toml instead of
# ~/.config/serviceconfig/serviceconfig.toml
settings, _ = load_settings(
    ServiceConfig,
    app_name="myservice"
)
```

### Using Custom Config Directory

```python
from pathlib import Path
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    api_url: str = "http://localhost"

# Look for config in /etc/myapp instead of current directory
settings, _ = load_settings(
    Config,
    app_name="myapp",
    cwd=Path("/etc/myapp")
)
```

## Development vs Production

### Environment-Specific Configuration

```python
from pydantic import BaseModel
from utilityhub_config import load_settings
import os

class Config(BaseModel):
    debug: bool = True
    database_url: str = "sqlite:///dev.db"
    log_level: str = "DEBUG"
    api_timeout: int = 30

# Load base configuration
settings, _ = load_settings(Config)

# Apply environment-specific overrides
if os.getenv("ENV") == "production":
    prod_overrides = {
        "debug": False,
        "database_url": "postgresql://prod.db/app",
        "log_level": "WARNING",
        "api_timeout": 10
    }
    settings, _ = load_settings(Config, overrides=prod_overrides)
else:
    print("Development mode enabled")
```

## Type Conversion Examples

### Automatic Type Conversion

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    port: int
    timeout: float
    enabled: bool
    tags: list[str]

# .env file:
# PORT=8080
# TIMEOUT=30.5
# ENABLED=true
# TAGS=api,web,service

settings, _ = load_settings(Config)
print(type(settings.port))     # <class 'int'>
print(type(settings.timeout)   # <class 'float'>
print(type(settings.enabled))  # <class 'bool'>
print(type(settings.tags))     # <class 'list'>
```

## Complete Real-World Example

```python
from pydantic import BaseModel, Field
from pathlib import Path
from utilityhub_config import load_settings
from utilityhub_config.errors import ConfigValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str
    pool_size: int = Field(default=10, gt=0)

class CacheConfig(BaseModel):
    enabled: bool = True
    ttl: int = Field(default=3600, gt=0)
    max_size: int = Field(default=1000, gt=0)

class AppConfig(BaseModel):
    app_name: str = "myapp"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    database: DatabaseConfig
    cache: CacheConfig
    workers: int = Field(default=4, gt=0)

def load_config() -> AppConfig:
    """Load application configuration with error handling."""
    try:
        settings, metadata = load_settings(
            AppConfig,
            app_name="myapp",
            cwd=Path.cwd(),
            env_prefix="MYAPP"
        )

        # Log configuration sources
        logger.info("Configuration loaded successfully")
        logger.debug("Configuration sources:")
        for field, source in metadata.per_field.items():
            logger.debug(f"  {field}: {source.source}")

        return settings

    except ConfigValidationError as e:
        logger.error(f"Configuration error:\n{e}")
        raise

if __name__ == "__main__":
    config = load_config()
    print(f"Running {config.app_name} v{config.app_version}")
    print(f"Debug mode: {config.debug}")
    print(f"Database: {config.database.host}:{config.database.port}")
    print(f"Cache enabled: {config.cache.enabled}")
```
