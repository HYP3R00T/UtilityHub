# Metadata Tracking

Track where each configuration value came from.

## Basic Usage

```python
settings, metadata = load_settings(Config)

source = metadata.get_source("database_url")
print(source.source)        # "env", "project", "defaults"
print(source.source_path)   # File path or "ENV:DATABASE_URL"
print(source.raw_value)     # Original value
```

## Audit All Settings

```python
for field in settings.model_fields:
    source = metadata.get_source(field)
    value = getattr(settings, field)
    print(f"{field}: {value} (from {source.source})")
```

## Find Environment Values

```python
env_fields = [
    field for field in settings.model_fields
    if metadata.get_source(field).source == "env"
]
print(f"From environment: {env_fields}")
```

## Debugging

```python
# Check if using production config
db_source = metadata.get_source("database_url")
if "production.yaml" in str(db_source.source_path):
    print("✓ Using production database")
```

[← Back to Guides](./index.md)
