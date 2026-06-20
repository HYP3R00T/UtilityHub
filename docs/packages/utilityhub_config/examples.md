---
icon: lucide/lightbulb
---

# Examples

This page shows fuller examples for `utilityhub_config` so teams can understand how to use it in real systems, not just in isolated snippets.

## What These Examples Show

The examples focus on common situations where configuration gets difficult:

- a local app that mixes defaults, files, and environment variables
- a service with nested settings and deployment-specific overrides
- a plugin-capable system that validates named extension blocks

## Example 1: Local Application With Files And Environment Variables

This pattern works well for developer tools, internal apps, and small services.

```python
from pydantic import BaseModel

from utilityhub_config import load_settings


class AppConfig(BaseModel):
    app_name: str = "reporter"
    database_url: str = "sqlite:///reports.db"
    debug: bool = False
    workers: int = 2


settings, metadata = load_settings(AppConfig, app_name="reporter")

print(settings.database_url)
print(settings.debug)
print(metadata.get_source("database_url").source)
```

How this behaves:

- defaults provide safe startup values
- project config files can override local behavior
- `.env` and environment variables can override for a specific machine or run

## Example 2: Service Configuration With Nested Models

This is a strong fit for web services or worker processes with grouped settings.

```python
from pydantic import BaseModel

from utilityhub_config import load_settings


class DatabaseConfig(BaseModel):
    url: str
    pool_size: int = 10


class ApiConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class ServiceConfig(BaseModel):
    app_name: str = "orders"
    debug: bool = False
    database: DatabaseConfig
    api: ApiConfig = ApiConfig()


settings, metadata = load_settings(ServiceConfig, app_name="orders")

print(settings.database.url)
print(settings.api.port)
print(metadata.get_source("database.url").source)
```

Why this helps in a larger system:

- related settings stay grouped together
- nested values still get source tracking
- startup validation catches missing required sections early

## Example 3: Explicit Production Config File

This is useful when deployment tooling passes a known configuration file path.

```python
from pathlib import Path
from pydantic import BaseModel

from utilityhub_config import load_settings


class Config(BaseModel):
    app_name: str = "billing"
    database_url: str
    debug: bool = False


settings, metadata = load_settings(
    Config,
    config_file=Path("/etc/billing/production.yaml"),
    app_name="billing",
)

print(settings.database_url)
print(metadata.get_source("database_url").source_path)
```

Why this helps:

- the config source is explicit
- production startup becomes easier to reason about
- file origin is preserved in metadata

## Example 4: Runtime Overrides In Tests Or Automation

This is useful when you need deterministic settings without modifying machine state.

```python
from pydantic import BaseModel

from utilityhub_config import load_settings


class Config(BaseModel):
    app_name: str = "importer"
    debug: bool = False
    workers: int = 4


settings, metadata = load_settings(
    Config,
    app_name="importer",
    overrides={
        "debug": True,
        "workers": 1,
    },
)

print(settings.debug)
print(settings.workers)
print(metadata.get_source("workers").source)
```

Why this helps:

- tests stay isolated from ambient environment state
- automation can make targeted adjustments safely
- override provenance remains visible in metadata

## Example 5: Plugin-Oriented System With Extension Schemas

This is the most useful pattern when your application has named dynamic sections.

```python
from pydantic import BaseModel

from utilityhub_config import load_settings


class StoragePluginConfig(BaseModel):
    bucket: str
    region: str = "us-east-1"


class SearchPluginConfig(BaseModel):
    endpoint: str
    index_name: str


class PlatformConfig(BaseModel):
    app_name: str = "platform"
    plugins: dict[str, object] = {}


settings, metadata = load_settings(
    PlatformConfig,
    app_name="platform",
    extension_root="plugins",
    extension_schemas={
        "storage": StoragePluginConfig,
        "search": SearchPluginConfig,
    },
)

storage = metadata.extension_configs["storage"]
search = metadata.extension_configs["search"]

print(storage.bucket)
print(search.index_name)
```

Why this helps in a complicated system:

- each named extension gets a validated schema
- plugin config stays dynamic without becoming unstructured
- metadata still tracks where extension values came from

## Quick Reference

```python
from pathlib import Path

from pydantic import BaseModel
from utilityhub_config import load_settings


class Config(BaseModel):
    database_url: str = "sqlite:///default.db"
    debug: bool = False


settings, metadata = load_settings(Config)
settings, _ = load_settings(Config, config_file=Path("./prod.yaml"))
settings, _ = load_settings(Config, env_prefix="MYAPP")
settings, _ = load_settings(Config, overrides={"debug": True})

source = metadata.get_source("database_url")
print(f"{source.source}: {source.source_path}")
```

## Local Demo Script

To validate nested metadata source tracking before publishing, run:

```bash
/workspaces/UtilityHub/.venv/bin/python examples/demo_utilityhub_config/main.py
```

[← Back to Documentation](./index.md)
