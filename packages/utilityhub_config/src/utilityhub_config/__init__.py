"""utilityhub_config

A small, deterministic configuration loader for modern Python applications.

This package provides type-safe configuration loading with clear precedence rules,
comprehensive metadata tracking, and detailed error reporting. It supports multiple
configuration sources and formats while maintaining predictable behavior.

Key Features:
- Type-safe configuration using Pydantic models
- Multi-source support: defaults, global config, project config, dotenv, env vars, overrides
- Clear precedence order with metadata tracking
- Support for TOML, YAML, and environment variable sources
- Rich error reporting with source information
- Path expansion utilities for configuration files

Example:
    ```python
    from pydantic import BaseModel
    from utilityhub_config import load_settings


    class Config(BaseModel):
        database_url: str = "sqlite:///default.db"
        debug: bool = False


    # Load configuration from all sources
    settings, metadata = load_settings(Config, app_name="myapp")

    # Access type-safe configuration
    print(settings.database_url)

    # Check where values came from
    source = metadata.get_source("database_url")
    print(f"Source: {source.source}")
    ```
"""

from utilityhub_config.api import get_config_path, load_settings
from utilityhub_config.utils import (
    expand_and_validate_path,
    expand_path,
    expand_path_validator,
)

__all__: list[str] = [
    "load_settings",
    "get_config_path",
    "expand_path",
    "expand_and_validate_path",
    "expand_path_validator",
]


def main() -> None:
    print("utilityhub-config: use `load_settings()` in your code")
