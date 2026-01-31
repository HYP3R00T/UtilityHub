# Environment Variables

## Basic Usage

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    database_url: str
    debug: bool = False
```

```bash
export DATABASE_URL=postgres://localhost/prod
export DEBUG=true
```

```python
settings, _ = load_settings(Config)
print(settings.database_url)  # postgres://localhost/prod
```

## With Prefix

```python
settings, _ = load_settings(Config, env_prefix="MYAPP")
```

```bash
export MYAPP_DATABASE_URL=postgres://localhost/prod
export MYAPP_DEBUG=true
```

## Field Naming

Python field → Environment variable:
- `database_url` → `DATABASE_URL`
- `max_workers` → `MAX_WORKERS`
- With prefix: `MYAPP_DATABASE_URL`

[← Back to Guides](./index.md)
