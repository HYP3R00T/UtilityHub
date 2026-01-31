# Error Handling

Handle configuration and validation errors.

## Error Types

### ConfigError
Raised when config file is missing or has wrong format.

```python
from utilityhub_config.errors import ConfigError

try:
    settings, _ = load_settings(Config, config_file=Path("missing.yaml"))
except ConfigError as e:
    print(f"Config error: {e}")
```

### ConfigValidationError
Raised when values fail Pydantic validation.

```python
from utilityhub_config.errors import ConfigValidationError

class Config(BaseModel):
    port: int

# .env has: PORT=not_a_number

try:
    settings, _ = load_settings(Config)
except ConfigValidationError as e:
    print(f"Validation error: {e}")
    print(f"Field: {e.field}")
    print(f"Value: {e.value}")
```

## Graceful Fallback

```python
try:
    settings, _ = load_settings(Config, config_file=Path("./prod.yaml"))
except ConfigError:
    # Fall back to defaults
    settings, _ = load_settings(Config)
```

## Required Fields

```python
class Config(BaseModel):
    database_url: str  # No default = required

try:
    settings, _ = load_settings(Config)
except ConfigValidationError as e:
    print(f"Missing required field: {e.field}")
```

[← Back to Guides](./index.md)
