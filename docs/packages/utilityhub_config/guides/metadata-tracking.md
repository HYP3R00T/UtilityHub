# Metadata Tracking

Track where each configuration value came from.

## Basic Usage

```python
settings, metadata = load_settings(Config)

source = metadata.get_source("database_url")
print(source.source)        # "env", "project", "defaults"
print(source.source_path)   # File path or "ENV:DATABASE_URL"
print(source.raw_value)     # Original value

# Nested path lookup
nested = metadata.get_source("database.host")
if nested:
    print(nested.source)      # "project", "env", "overrides", ...
    print(nested.source_path) # File path or "ENV:DATABASE__HOST"
```

`get_source()` supports dotted paths for nested settings.

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
    if metadata.get_source(field) and metadata.get_source(field).source == "env"
]
print(f"From environment: {env_fields}")
```

For nested models, you can inspect known nested paths directly:

```python
for path in ["model.backend", "model.device", "inference.despill_strength"]:
    src = metadata.get_source(path)
    if src and src.source == "env":
        print(f"{path} from {src.source_path}")
```

## Debugging

```python
# Check if using production config
db_source = metadata.get_source("database_url")
if db_source and "production.yaml" in str(db_source.source_path):
    print("✓ Using production database")
```

[← Back to Guides](./index.md)
