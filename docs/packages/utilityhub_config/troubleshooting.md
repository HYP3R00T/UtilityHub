---
icon: lucide/wrench
---

# Troubleshooting

## Configuration Not Loading

### Files Aren't Being Picked Up

Check which files are being searched:

```python
from utilityhub_config.errors import ConfigValidationError

try:
    settings, _ = load_settings(Config)
except ConfigValidationError as e:
    print("Checked files:")
    for file in e.checked_files:
        print(f"  - {file}")
```

**Solution:** Move your config files to one of the checked locations.

### Wrong App Name Derived

By default, the app name comes from your model class:

```python
class MyAppConfig(BaseModel):  # App name derived: "myappconfig"
    pass
```

This looks for `~/.config/myappconfig/myappconfig.toml`.

**Solution:** Specify explicit app name:

```python
settings, _ = load_settings(MyAppConfig, app_name="myapp")
# Now looks for ~/.config/myapp/myapp.toml
```

## Environment Variables Not Working

### Variable Not Found

Environment variables must match field names (uppercase):

```python
class Config(BaseModel):
    api_key: str     # Looks for API_KEY environment variable
    db_url: str      # Looks for DB_URL environment variable
```

**Check:**
```bash
echo $API_KEY      # Is it set?
echo $DB_URL       # Is it set?
```

### Using Prefix and Variables Ignored

With a prefix, only prefixed variables are checked:

```python
# With prefix="MYAPP", only looks for:
# MYAPP_API_KEY, MYAPP_DB_URL
# Does NOT look for API_KEY or DB_URL

settings, _ = load_settings(
    Config,
    env_prefix="MYAPP"
)
```

**Solution:** Either set prefixed variables or remove the prefix.

### Case Sensitivity

Environment variable names are case-sensitive on Linux/Mac:

```bash
export api_key="value"   # Won't work
export API_KEY="value"   # Correct
```

## Type Conversion Errors

### "value is not a valid integer" Error

Values from .env and environment are strings and must be convertible:

```python
class Config(BaseModel):
    port: int

# .env
PORT=8080        # Correct - string "8080" converts to int
PORT=invalid     # ERROR - can't convert "invalid" to int
```

**Solution:** Ensure values can be converted to the declared type.

### Boolean Values Not Converting

Boolean strings must be recognized values:

```python
# Recognized as True:
DEBUG=true
DEBUG=True
DEBUG=1

# Recognized as False:
DEBUG=false
DEBUG=False
DEBUG=0
```

**Tip:** Use lowercase `true`/`false` in .env files for consistency.

### List/Array Values

TOML and YAML support lists naturally:

```toml
# TOML
tags = ["api", "web", "service"]
```

```yaml
# YAML
tags:
  - api
  - web
  - service
```

For .env files, individual items don't convert to lists. You'd need to use JSON:

```bash
# .env - use JSON syntax (if your model supports it)
TAGS='["api","web","service"]'
```

## Validation Errors

### Missing Required Field

If a field has no default and isn't provided:

```python
class Config(BaseModel):
    api_key: str  # No default!

# Error: "api_key" is required
settings, _ = load_settings(Config)
```

**Solution:** Either provide a default or set it in config/environment:

```python
# Option 1: Add default
class Config(BaseModel):
    api_key: str = "default_key"

# Option 2: Provide in config file or environment
os.environ["API_KEY"] = "my_key"
```

### Constraint Violations

Pydantic validators are enforced:

```python
from pydantic import BaseModel, Field

class Config(BaseModel):
    port: int = Field(gt=0, lt=65536)  # Valid port range

# .env
PORT=-1  # ERROR: less than 0
```

**Solution:** Ensure values satisfy constraints.

## Precedence Issues

### Settings Not Being Overridden

Remember the precedence order (lowest to highest):

1. Defaults
2. Global config
3. Project config
4. .env
5. Environment variables
6. Runtime overrides

If a higher level is set, lower levels are ignored:

```python
class Config(BaseModel):
    debug: bool = False

# Global config: debug = true
# Project config: debug = false  # This wins, overrides global
```

**Solution:** Check which level is setting your value:

```python
settings, metadata = load_settings(Config)
source = metadata.get_source("debug")
print(f"debug came from: {source.source}")
```

## File Format Issues

### TOML Syntax Errors

TOML has strict syntax:

```toml
# Wrong - unquoted string
app_name = myapp

# Correct
app_name = "myapp"

# Wrong - invalid key
my-setting = "value"

# Correct - use underscore or alphanumeric
my_setting = "value"
```

### YAML Indentation

YAML is indentation-sensitive:

```yaml
# Wrong - inconsistent indentation
database:
  host: localhost
    port: 5432

# Correct
database:
  host: localhost
  port: 5432
```

Use spaces (not tabs) for indentation.

### Nested Structure Mismatch

Ensure nested config matches your model:

```python
class DatabaseConfig(BaseModel):
    host: str
    port: int

class Config(BaseModel):
    database: DatabaseConfig
```

```toml
# Correct structure
[database]
host = "localhost"
port = 5432

# Wrong - missing nesting
database_host = "localhost"  # Doesn't match model
```

## Debugging Configuration Loading

### Enable Detailed Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

from utilityhub_config import load_settings

settings, metadata = load_settings(Config)
```

### Print All Sources

```python
settings, metadata = load_settings(Config)

print("Configuration sources:")
for field, source in metadata.per_field.items():
    print(f"  {field}:")
    print(f"    Source: {source.source}")
    print(f"    Path: {source.source_path}")
    print(f"    Value: {source.raw_value}")
```

### Check Files Searched

```python
from utilityhub_config.errors import ConfigValidationError

try:
    settings, _ = load_settings(Config)
except ConfigValidationError as e:
    print("Files searched:")
    for file in e.checked_files:
        print(f"  {file}")
```

## Common Patterns for Solutions

### Problem: "Settings work in dev, not in production"

**Cause:** Different app name, missing environment variables, or wrong config directory.

**Solution:**
```python
# Explicitly specify everything
settings, _ = load_settings(
    Config,
    app_name="myapp",           # Same across all environments
    cwd=Path("/etc/myapp"),     # Production config location
    env_prefix="MYAPP"          # Consistent prefix
)
```

### Problem: "I can't tell where a setting came from"

**Solution:**
```python
settings, metadata = load_settings(Config)

# Check a specific field
source = metadata.get_source("api_key")
if source:
    print(f"Source: {source.source}")
    print(f"Path: {source.source_path}")
    print(f"Value: {source.raw_value}")
```

### Problem: "I'm accidentally overriding production config locally"

**Cause:** Environment variables or .env file overriding intended config.

**Solution:** Be explicit about precedence:
```python
# Avoid loading .env in production
import os
if not os.getenv("PRODUCTION"):
    # Only load .env in development
    settings, _ = load_settings(Config)
```

Or use explicit overrides:
```python
overrides = {}
if os.getenv("ENV") == "production":
    overrides = {
        "database_url": "postgresql://prod.db/app",
        "debug": False
    }

settings, _ = load_settings(Config, overrides=overrides)
```

## Getting Help

If you can't resolve the issue:

1. **Check file locations** - Print `checked_files` list
2. **Check sources** - Use `metadata.per_field` to see where values come from
3. **Enable logging** - Set `logging.basicConfig(level=logging.DEBUG)`
4. **Verify types** - Ensure config values match Pydantic model types
5. **Check precedence** - Remember that environment variables override .env
