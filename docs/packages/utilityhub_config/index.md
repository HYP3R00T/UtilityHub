---
icon: lucide/settings
---

# utilityhub_config

A **deterministic, typed configuration loader** for modern Python applications. Load settings from multiple sources with clear precedence, comprehensive metadata tracking, and detailed validation errors.

## Why This Package Exists

Application configuration often becomes messy as projects grow.

Teams usually end up rebuilding the same logic over and over:

- reading values from multiple places
- deciding which source wins
- converting string values into typed application settings
- explaining where a value came from during debugging
- handling invalid or missing configuration clearly

`utilityhub_config` exists to make that layer explicit, typed, and predictable.

## What Problem It Solves

Without a dedicated configuration layer, teams often run into a few recurring pain points:

- configuration scattered across files, environment variables, and ad hoc code
- precedence rules that are implied rather than documented
- hard-to-debug startup failures when values are missing or malformed
- no clear way to see whether a value came from defaults, a file, `.env`, or the environment
- repetitive setup code every time a new app or service is created

`utilityhub_config` solves this by giving you one deterministic loading flow with typed validation and source tracking.

## What It Does

`utilityhub_config` resolves application configuration from multiple sources in a strict, explicit precedence order. Instead of magic or implicit behavior, you get:

- ✅ **Type-safe configuration** - Full Pydantic v2+ validation
- ✅ **Multi-source support** - TOML, YAML, .env, environment variables, runtime overrides
- ✅ **Utility functions** - Get canonical config paths with `get_config_path()`
- ✅ **Metadata tracking** - Know exactly where each setting came from
- ✅ **Deterministic resolution** - Clear, predictable precedence order
- ✅ **Rich error reporting** - Validation failures include sources, files checked, and precedence info

## Feature Highlights

- **Single loading entrypoint** with `load_settings()`
- **Strong typing** through Pydantic models
- **File-based config support** for TOML and YAML
- **Environment-aware loading** through `.env` files and environment variables
- **Runtime overrides** for tests, scripts, and programmatic control
- **Source metadata** for auditability and debugging
- **Extension schemas** for validating named runtime sections
- **Path utilities** for canonical config file handling

## Quick Start

```bash
uv add utilityhub_config
```

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    database_url: str = "sqlite:///default.db"
    debug: bool = False

# Load and validate configuration
settings, metadata = load_settings(Config)

# Type-safe access
print(settings.database_url)

# Track where it came from
print(f"Source: {metadata.get_source('database_url').source}")
```

## Documentation

### Getting Started
- [Installation & Quick Start](./getting-started.md) - Set up in 5 minutes

### Understanding How It Works
- [Precedence Order](./concepts/precedence.md) - How sources are prioritized
- [Metadata Tracking](./concepts/metadata.md) - Understanding field origins

### Usage Guides
- [Basic Usage](./guides/basic-usage.md) - First steps with load_settings
- [Configuration Files](./guides/configuration-files.md) - TOML, YAML, .env formats
- [Config Paths](./guides/config-paths.md) - Get config paths with get_config_path (NEW!)
- [Environment Variables](./guides/environment-variables.md) - Using env vars
- [Explicit Config Files](./guides/explicit-config-files.md) - Load specific file paths (NEW!)
- [Path Expansion](./guides/path-expansion.md) - Expand `~` and `$VAR` in paths
- [Runtime Overrides](./guides/runtime-overrides.md) - Programmatic configuration
- [Nested Models](./guides/nested-models.md) - Complex configurations
- [Metadata Tracking](./guides/metadata-tracking.md) - Practical metadata usage
- [Error Handling](./guides/error-handling.md) - Handling validation errors

### Examples & Help
- [Examples](./examples.md) - Realistic scenarios for apps, services, tests, and plugin systems

## Key Concepts at a Glance

**Precedence Order** (lowest to highest):
```
Defaults < Global Config < Project Config < Dotenv < Environment Vars < Overrides
```

**Metadata Tracking:**
```python
source = metadata.get_source("database_url")
print(source.source)        # Where it came from
print(source.source_path)   # File path or env var name
print(source.raw_value)     # Original value
```

## Where to Go Next

👉 **New here?** Start with [Getting Started](./getting-started.md)

👉 **Want to learn the design?** Read [Precedence Order](./concepts/precedence.md)

👉 **Ready to code?** Jump to [Usage Guides](./guides/index.md)

👉 **Looking for examples?** Check [Examples](./examples.md)
