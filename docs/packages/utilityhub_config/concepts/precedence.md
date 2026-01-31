# Precedence Order

Values are loaded in order. **Later sources override earlier ones.**

## The Order

```python
settings, metadata = load_settings(Config)
```

1. **Model defaults** — Field defaults in your Pydantic model
2. **Global config** — `~/.config/config/config.yaml` or `.toml`
3. **Project config** — `./config.yaml` or `./config.toml` in current directory
4. **`.env` file** — `DATABASE_URL=...` in `./.env`
5. **Environment variables** — `export DATABASE_URL=...`
6. **Runtime overrides** — `overrides={"database_url": "..."}`

## Example

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    workers: int = 4  # 1. Default

# 2. ~/.config/config/config.yaml contains: workers: 6
# 3. ./config.yaml contains: workers: 8
# 4. .env contains: WORKERS=10
# 5. Environment has: export WORKERS=12

settings, _ = load_settings(Config)
print(settings.workers)  # 12 (environment wins)

# 6. Runtime override wins over everything
settings, _ = load_settings(Config, overrides={"workers": 16})
print(settings.workers)  # 16
```

## Skip Auto-Discovery

Use `config_file` to load only a specific file:

```python
from pathlib import Path

settings, _ = load_settings(
    Config,
    config_file=Path("./production.yaml")
)
# Only loads: defaults → production.yaml → .env → env → overrides
# Skips: global config, project auto-discovery
```

[← Back to Concepts](./index.md)
