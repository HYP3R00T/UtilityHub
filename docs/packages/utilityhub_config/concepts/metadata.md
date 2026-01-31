# Metadata Tracking

Every field tracks where its value came from.

## Basic Usage

```python
settings, metadata = load_settings(Config)

source = metadata.get_source("database_url")
print(source.source)        # "env", "project", "defaults", etc.
print(source.source_path)   # Full path or "ENV:DATABASE_URL"
print(source.raw_value)     # Original value before validation
```

## Source Types

- `"defaults"` — From model field defaults
- `"global"` — From `~/.config/config/config.yaml`
- `"project"` — From `./config.yaml` or explicit `config_file`
- `"dotenv"` — From `.env` file
- `"env"` — From environment variables
- `"overrides"` — From runtime `overrides` parameter

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
    if source.source == "env":
        print(f"{field} came from {source.source_path}")
```

[← Back to Concepts](./index.md)
