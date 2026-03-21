# Metadata Tracking

Every field tracks where its value came from.

## Basic Usage

```python
settings, metadata = load_settings(Config)

source = metadata.get_source("database_url")
print(source.source)        # "env", "project", "defaults", etc.
print(source.source_path)   # Full path or "ENV:DATABASE_URL"
print(source.raw_value)     # Original value before validation

# Nested field paths are supported
nested = metadata.get_source("database.host")
print(nested.source)        # "project", "env", "overrides", etc.
print(nested.source_path)   # Full path or "ENV:DATABASE__HOST"
```

If a nested field was not tracked directly, `get_source("a.b.c")` falls back to
the nearest tracked parent path.

## Source Types

- `"defaults"` - From model field defaults
- `"global"` - From global app config files (for example `~/.config/<app>/<app>.yaml`)
- `"project"` - From `./config.yaml` or explicit `config_file`
- `"dotenv"` - From `.env` file
- `"env"` - From environment variables
- `"overrides"` - From runtime `overrides` parameter

## Example: Configuration Audit

```python
def audit_config(settings, metadata):
    for field in settings.model_fields:
        source = metadata.get_source(field)
        value = getattr(settings, field)
        print(f"{field}: {value} (from {source.source})")

settings, metadata = load_settings(Config)
audit_config(settings, metadata)
```

## Example: Nested Configuration Audit

```python
for path in [
    "model.backend",
    "model.device",
    "inference.despill_strength",
]:
    source = metadata.get_source(path)
    if source is None:
        print(f"{path}: source not found")
        continue
    print(f"{path}: {source.source} ({source.source_path})")
```

Output:
```
database_url: postgres://prod (from env)
debug: False (from defaults)
workers: 8 (from project)
```

## Debugging

```python
# Find all environment-sourced values
for field in settings.model_fields:
    source = metadata.get_source(field)
    if source and source.source == "env":
        print(f"{field} came from {source.source_path}")
```

[← Back to Concepts](./index.md)
