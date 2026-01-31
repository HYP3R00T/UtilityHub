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

settings, _ = load_settings(Config)
print(settings.database.host)
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

## With Prefix

```python
settings, _ = load_settings(Config, env_prefix="MYAPP")
```

```bash
export MYAPP_DATABASE__HOST=prod.example.com
```

[← Back to Guides](./index.md)
