# Nested Models

Use nested Pydantic models for complex configurations.

## Basic Nested Model

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "mydb"

class Config(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    debug: bool = False

settings, metadata = load_settings(Config)
print(settings.database.host)
print(metadata.get_source("database.host").source)
```

## Config File

`config.yaml`:
```yaml
database:
  host: prod.example.com
  port: 5432
  name: production
debug: false
```

## Environment Variables

```bash
export DATABASE__HOST=prod.example.com
export DATABASE__PORT=5432
export DATABASE__NAME=production
```

Note: Use double underscores (`__`) for nesting.

These values are tracked as nested metadata paths:

```python
settings, metadata = load_settings(Config)

source = metadata.get_source("database.host")
if source:
  print(source.source)      # "env"
  print(source.source_path) # "ENV:DATABASE__HOST"
```

## With Prefix

```python
settings, _ = load_settings(Config, env_prefix="MYAPP")
```

```bash
export MYAPP_DATABASE__HOST=prod.example.com
```

## Runtime Overrides for Nested Fields

```python
settings, metadata = load_settings(
    Config,
    overrides={"database": {"host": "runtime.example.com"}},
)

print(settings.database.host)                            # runtime.example.com
source = metadata.get_source("database.host")
if source:
    print(source.source)      # overrides
    print(source.source_path) # runtime
```

[← Back to Guides](./index.md)
