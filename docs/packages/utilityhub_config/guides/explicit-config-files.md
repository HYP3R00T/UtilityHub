# Explicit Config Files

Load a specific config file instead of auto-discovery.

## Basic Usage

```python
from pathlib import Path
from utilityhub_config import load_settings

settings, _ = load_settings(
    Config,
    config_file=Path("./production.yaml")
)
```

## Format Detection

Automatically detected from extension:
- `.yaml`, `.yml` → YAML format
- `.toml` → TOML format

```python
# Both work automatically
load_settings(Config, config_file=Path("./prod.yaml"))
load_settings(Config, config_file=Path("./prod.toml"))
```

## Precedence

When using `config_file`, auto-discovery is skipped:

**Without `config_file`:**
defaults → global config → project config → .env → env → overrides

**With `config_file`:**
defaults → **specified file** → .env → env → overrides

## Error Handling

```python
from utilityhub_config.errors import ConfigError

try:
    settings, _ = load_settings(Config, config_file=Path("./missing.yaml"))
except ConfigError as e:
    print(f"Error: {e}")
```

[← Back to Guides](./index.md)
