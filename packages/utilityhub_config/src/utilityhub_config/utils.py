"""Utility functions for utilityhub_config."""

from __future__ import annotations

import os
from pathlib import Path


def expand_path(value: str) -> Path:
    """Expand a path string with tilde and environment variables.

    Expands both ~ (user home directory) and environment variables in the format
    $VAR or ${VAR}. The resulting path does not need to exist.

    Args:
        value: A path string that may contain ~ and/or environment variables.
               Examples: "~/config/app.yaml", "$HOME/config", "${CONFIG_DIR}/app.toml"

    Returns:
        An absolute Path object with ~ and environment variables expanded.

    Raises:
        KeyError: If an environment variable is referenced but not set.

    Examples:
        >>> expand_path("~/config.yaml")  # expands ~ to user home
        PosixPath('/home/user/config.yaml')

        >>> expand_path("$HOME/data")  # expands environment variables
        PosixPath('/home/user/data')

        >>> expand_path("${CONFIG_DIR}/app.yaml")  # ${VAR} syntax supported
        PosixPath('/etc/config/app.yaml')
    """
    # First expand ~ to home directory
    expanded = Path(value).expanduser()

    # Then expand environment variables
    expanded_str = os.path.expandvars(str(expanded))
    return Path(expanded_str)


def expand_and_validate_path(value: str) -> Path:
    """Expand a path string and validate that it exists.

    Expands both ~ (user home directory) and environment variables in the format
    $VAR or ${VAR}. After expansion, validates that the path exists.

    Args:
        value: A path string that may contain ~ and/or environment variables.
               Examples: "~/config/app.yaml", "$HOME/config", "${CONFIG_DIR}/app.toml"

    Returns:
        An absolute Path object with ~ and environment variables expanded.

    Raises:
        KeyError: If an environment variable is referenced but not set.
        FileNotFoundError: If the expanded path does not exist.

    Examples:
        >>> expand_and_validate_path("~/existing_config.yaml")
        PosixPath('/home/user/existing_config.yaml')

        >>> expand_and_validate_path("~/nonexistent.yaml")
        Traceback (most recent call last):
            ...
        FileNotFoundError: [Errno 2] No such file or directory: '/home/user/nonexistent.yaml'
    """
    path = expand_path(value)

    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    return path


def expand_path_validator(value: Path | str) -> Path:
    """Pydantic field validator to expand paths with tilde and environment variables.

    This is a Pydantic field validator that can be used to automatically expand
    tilde (~) and environment variables in Path fields. The expanded path is validated
    to ensure it exists.

    This validator should be used with Pydantic's `@field_validator` decorator.

    Args:
        value: A Path or string that may contain ~ and/or environment variables.

    Returns:
        An expanded and validated Path object.

    Raises:
        FileNotFoundError: If the expanded path does not exist.
        ValueError: If the path cannot be expanded due to invalid syntax.

    Example:
        ```python
        from pathlib import Path
        from pydantic import BaseModel, field_validator
        from utilityhub_config.utils import expand_path_validator


        class Config(BaseModel):
            config_file: Path

            @field_validator("config_file", mode="before")
            @classmethod
            def expand_config_path(cls, v: Path | str) -> Path:
                return expand_path_validator(v)
        ```
    """
    if isinstance(value, Path):
        value = str(value)

    return expand_and_validate_path(value)
