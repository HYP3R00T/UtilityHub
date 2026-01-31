# Basic Usage

## Install

```bash
pip install utilityhub_config
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

## With App Name

```python
settings, _ = load_settings(Config, app_name="myapp")
# Looks for ~/.config/myapp/config.yaml
# Looks for ./myapp.yaml or ./myapp.toml
```

## Check Sources

```python
settings, metadata = load_settings(Config)
source = metadata.get_source("database_url")
print(f"{source.source}: {source.source_path}")
```

[← Back to Guides](./index.md)
