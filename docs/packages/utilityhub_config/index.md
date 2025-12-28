---
icon: lucide/settings
---

# utilityhub_config

A **deterministic, typed configuration loader** for modern Python applications. Load settings from multiple sources with clear precedence, comprehensive metadata tracking, and detailed validation errors.

## What It Does

`utilityhub_config` resolves application configuration from multiple sources in a strict, explicit precedence order. Instead of magic or implicit behavior, you get:

- ✅ **Type-safe configuration** - Full Pydantic v2+ validation
- ✅ **Multi-source support** - TOML, YAML, .env, environment variables, runtime overrides
- ✅ **Metadata tracking** - Know exactly where each setting came from
- ✅ **Deterministic resolution** - Clear, predictable precedence order
- ✅ **Rich error reporting** - Validation failures include sources, files checked, and precedence info

## Key Concepts

### Precedence Order

Settings are resolved from **lowest to highest** priority:

1. **Defaults** - Field defaults from your Pydantic model
2. **Global config** - `~/.config/{app_name}/{app_name}.{toml,yaml}`
3. **Project config** - `{cwd}/{app_name}.{toml,yaml}` or `{cwd}/config/*.{toml,yaml}`
4. **Dotenv** - `.env` file in current directory
5. **Environment variables** - `{APP_NAME}_{FIELD_NAME}` or `{FIELD_NAME}`
6. **Runtime overrides** - Passed via `overrides` parameter (highest priority)

Higher levels override lower levels. Only sources that exist are consulted.

### Metadata Tracking

Every loaded setting carries metadata about its source:

```python
source = metadata.get_source("database_url")
print(f"Source: {source.source}")        # "env", "project", "overrides", etc.
print(f"Path: {source.source_path}")     # File path or "ENV:VARIABLE_NAME"
print(f"Value: {source.raw_value}")      # Original value before validation
```

## Installation

```bash
pip install utilityhub_config
```

## Quick Start

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class AppConfig(BaseModel):
    database_url: str = "sqlite:///dev.db"
    debug: bool = False
    workers: int = 4

# Load settings from all sources
settings, metadata = load_settings(AppConfig)

# Use type-safe settings
print(settings.database_url)
print(settings.workers)  # Automatically converted to int

# Check where a setting came from
db_source = metadata.get_source("database_url")
print(f"Database URL came from: {db_source.source}")
```

## API Reference

### `load_settings()`

Load and validate settings from multiple sources.

```python
def load_settings[T: BaseModel](
    model: type[T],
    *,
    app_name: str | None = None,
    cwd: Path | None = None,
    env_prefix: str | None = None,
    overrides: dict[str, Any] | None = None,
) -> tuple[T, SettingsMetadata]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `type[T]` | A Pydantic `BaseModel` subclass (required) |
| `app_name` | `str \| None` | Application name for config files. Defaults to lowercased model class name |
| `cwd` | `Path \| None` | Working directory for config search. Defaults to current directory |
| `env_prefix` | `str \| None` | Prefix for environment variables (e.g., `'MYAPP_'` looks for `MYAPP_DATABASE_URL`) |
| `overrides` | `dict[str, Any] \| None` | Runtime overrides (highest precedence) |

**Returns:**

- `tuple[T, SettingsMetadata]` - Validated settings instance and metadata

**Raises:**

- `ConfigValidationError` - If validation fails, with detailed context

### `SettingsMetadata`

Tracks where each setting came from.

```python
@dataclass
class SettingsMetadata:
    per_field: dict[str, FieldSource]

    def get_source(self, field: str) -> FieldSource | None:
        """Get source information for a specific field."""
```

### `FieldSource`

Metadata for a single field.

```python
@dataclass(frozen=True)
class FieldSource:
    source: str              # "defaults", "global", "project", "dotenv", "env", "overrides"
    source_path: str | None  # File path, "ENV:VARIABLE_NAME", or "runtime"
    raw_value: Any          # Original value before validation
```

### `ConfigValidationError`

Raised when validation fails with rich context.

```python
@dataclass
class ConfigValidationError(ConfigError):
    message: str
    errors: ValidationError
    metadata: SettingsMetadata
    checked_files: Iterable[str]
    precedence: list[str]
```

## Common Patterns

### Basic Setup

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    database_url: str
    debug: bool = False

settings, _ = load_settings(Config)
```

### With Custom App Name

```python
settings, metadata = load_settings(
    Config,
    app_name="myapp",
    cwd=Path("/etc/myapp")
)
```

### With Environment Prefix

```python
settings, _ = load_settings(
    Config,
    env_prefix="MYAPP"
    # Now looks for MYAPP_DATABASE_URL, MYAPP_DEBUG, etc.
)
```

### Runtime Overrides

```python
settings, _ = load_settings(
    Config,
    overrides={
        "debug": True,
        "database_url": "postgresql://..."
    }
)
```

### Error Handling

```python
from utilityhub_config.errors import ConfigValidationError

try:
    settings, metadata = load_settings(Config)
except ConfigValidationError as e:
    print(e)  # Rich output with sources and file locations
```

## Documentation

- **[Getting Started](./getting-started.md)** — Installation and setup
- **[Examples](./examples.md)** — Practical usage examples
- **[Configuration Files](./config-files.md)** — TOML, YAML, .env formats
- **[Troubleshooting](./troubleshooting.md)** — Common issues and solutions

## Design Philosophy

- **Zero magic** — Explicit precedence, no hidden behavior
- **Type safety first** — Pydantic validation required
- **Transparency** — Metadata on every setting
- **Deterministic** — Same config always produces same result
- **Fail loudly** — Clear error messages when validation fails
