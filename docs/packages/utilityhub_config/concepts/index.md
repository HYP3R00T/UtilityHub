# Core Concepts

## Precedence Order

Values are loaded in this order (later wins):

1. Model defaults
2. Global config (`~/.config/config/`)
3. Project config (`./config.yaml` or `./config.toml`)
4. `.env` file
5. Environment variables
6. Runtime overrides

[Read more →](./precedence.md)

## Metadata Tracking

Every field tracks where its value came from:

```python
settings, metadata = load_settings(Config)
source = metadata.get_source("database_url")
print(source.source)        # "env", "project", "defaults", etc.
print(source.source_path)   # File path or "ENV:DATABASE_URL"
```

[Read more →](./metadata.md)
