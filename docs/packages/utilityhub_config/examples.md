---
icon: lucide/lightbulb
---

# Examples

All examples are in the usage guides:

## Getting Started
- [Basic Usage](./guides/basic-usage.md) — First steps with `load_settings()`
- [Configuration Files](./guides/configuration-files.md) — TOML, YAML, .env formats

## Common Tasks
- [Environment Variables](./guides/environment-variables.md) — Use env vars with prefixes
- [Explicit Config Files](./guides/explicit-config-files.md) — Load specific files
- [Runtime Overrides](./guides/runtime-overrides.md) — Override at runtime
- [Nested Models](./guides/nested-models.md) — Complex configurations

## Advanced
- [Metadata Tracking](./guides/metadata-tracking.md) — Track value sources
- [Error Handling](./guides/error-handling.md) — Handle validation errors

## Quick Reference

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    database_url: str = "sqlite:///default.db"
    debug: bool = False

# Basic usage
settings, metadata = load_settings(Config)

# With config file
settings, _ = load_settings(Config, config_file=Path("./prod.yaml"))

# With prefix
settings, _ = load_settings(Config, env_prefix="MYAPP")

# With overrides
settings, _ = load_settings(Config, overrides={"debug": True})

# Check source
source = metadata.get_source("database_url")
print(f"{source.source}: {source.source_path}")
```

[← Back to Documentation](./index.md)
