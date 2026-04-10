# utilityhub_config

`utilityhub_config` is a lightweight, deterministic configuration loader for Python applications.
It resolves values from defaults, configuration files, dotenv, environment variables, and runtime overrides with explicit precedence and metadata.

## Why use this package?

- Pydantic validation for configuration values
- Explicit precedence order across multiple sources
- Metadata tracking of where each field came from
- TOML, YAML, `.env`, and environment variable support
- Optional env var loading via `env_vars=False`
- Explicit config file support with `config_file`
- Runtime schema validation for dynamic sections using `extension_schemas`

## Install

```bash
pip install utilityhub_config
```

## Basic usage

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class Config(BaseModel):
    database_url: str = "sqlite:///default.db"
    debug: bool = False

settings, metadata = load_settings(Config)
```

## Documentation

This package is documented on the website. For complete usage and examples, see [utilityhub_config](https://utilityhub.hyperoot.dev/packages/utilityhub_config/).

## Notes

- `config_file` loads a single explicit file and skips project auto-discovery.
- `env_vars=False` disables environment variable lookup entirely.
- `extension_schemas` supports runtime-registered named sections under a configurable root.

## License

See the project LICENSE file.
