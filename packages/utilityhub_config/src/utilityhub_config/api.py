from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ValidationError

from utilityhub_config.errors import ConfigValidationError
from utilityhub_config.metadata import SettingsMetadata
from utilityhub_config.resolver import PrecedenceResolver

T = TypeVar("T", bound=BaseModel)


def load_settings[T: BaseModel](
    model: type[T],
    *,
    app_name: str | None = None,
    cwd: Path | None = None,
    env_prefix: str | None = None,
    config_file: Path | None = None,
    overrides: dict[str, Any] | None = None,
) -> tuple[T, SettingsMetadata]:
    """Load and validate settings for the given Pydantic model.

    Resolves configuration from multiple sources in precedence order:
    defaults → global config → [explicit file OR project config] → dotenv → environment variables → runtime overrides.

    Args:
        model: A Pydantic BaseModel subclass to validate and populate.
        app_name: Application name for config file lookup (defaults to model class name).
        cwd: Working directory for config file search (defaults to current directory).
        env_prefix: Optional prefix for environment variable lookup (e.g., 'MYAPP_').
        config_file: Explicit config file path to load as project config. If provided, skips auto-discovery
                    of {app_name}.yaml/.toml in standard locations and loads this file instead. File format
                    is auto-detected from extension (.yaml, .yml, or .toml). Still respects precedence order -
                    environment variables and overrides can override values from this file. Must exist and be
                    readable. (Optional)
        overrides: Runtime overrides as a dictionary (highest precedence).

    Returns:
        A tuple of (settings_instance, metadata) where settings_instance is an instance
        of the provided model type, and metadata tracks which source provided each field.

    Raises:
        ConfigValidationError: If validation fails, with detailed context about sources and files checked.
        ConfigError: If config_file is provided but doesn't exist, is not a file, or has an unsupported format.
    """
    cwd = Path.cwd() if cwd is None else cwd
    if config_file is not None:
        config_file = config_file.resolve()

    resolver = PrecedenceResolver(app_name=app_name, cwd=cwd, env_prefix=env_prefix, config_file=config_file)

    merged, metadata, checked_files = resolver.resolve(model=model, overrides=overrides or {})

    try:
        instance = model.model_validate(merged)
    except ValidationError as exc:  # pydantic v2
        raise ConfigValidationError(
            "Validation failed",
            errors=exc,
            metadata=metadata,
            checked_files=checked_files,
            precedence=resolver.precedence_order,
        ) from exc

    return instance, metadata


def get_config_path(
    app_name: str,
    format: Literal["toml", "yaml"] = "toml",
) -> Path:
    """Get the canonical global config path for an application.

    Returns the standard location where the application's global configuration
    file should be stored: ~/.config/{app_name}/{app_name}.{format}

    This function mirrors the logic used internally by PrecedenceResolver._global_config_paths(),
    ensuring consistency between this utility and the configuration loading system.

    Args:
        app_name: The application name (used in directory and file names).
        format: The configuration file format. Supported values are "toml" (default)
                and "yaml". The format determines the file extension.

    Returns:
        A Path object representing the canonical config file location.
        Note: The path is not validated for existence; the caller determines
        what to do next (e.g., load, create, or overwrite).

    Examples:
        >>> from utilityhub_config import get_config_path
        >>> path = get_config_path("myapp")
        >>> str(path)  # doctest: +ELLIPSIS
        '.../.config/myapp/myapp.toml'
        >>> yaml_path = get_config_path("myapp", format="yaml")
        >>> str(yaml_path)  # doctest: +ELLIPSIS
        '.../.config/myapp/myapp.yaml'
    """
    if format not in ("toml", "yaml"):
        raise ValueError("Unsupported format: {format}. Supported formats: toml, yaml")

    home = Path.home()
    config_dir = home / ".config" / app_name
    return config_dir / f"{app_name}.{format}"


def write_config(
    app_name: str,
    data: dict[str, Any],
    format: Literal["toml", "yaml"] = "toml",
) -> Path:
    """Write configuration data to the standard global config file location.

    Writes the provided configuration data to ~/.config/{app_name}/{app_name}.{format}.
    Creates the directory structure if it doesn't exist.

    Args:
        app_name: The application name (used in directory and file names).
        data: The configuration data to write as a dictionary.
        format: The configuration file format. Supported values are "toml" (default)
                and "yaml".

    Returns:
        The Path to the written configuration file.

    Raises:
        ValueError: If the format is not supported.
        OSError: If writing to the file fails.

    Examples:
        >>> from utilityhub_config import write_config
        >>> config_data = {"database": {"url": "sqlite:///app.db"}, "debug": True}
        >>> path = write_config("myapp", config_data)
        >>> str(path)  # doctest: +ELLIPSIS
        '.../.config/myapp/myapp.toml'
    """
    config_path = get_config_path(app_name, format=format)

    # Create parent directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the data based on format
    if format == "yaml":
        import yaml

        with config_path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    elif format == "toml":
        try:
            import tomli_w
        except ImportError:
            raise ImportError("tomli_w is required for TOML writing. Install it with: pip install tomli_w") from None
        with config_path.open("wb") as f:
            tomli_w.dump(data, f)
    else:
        raise ValueError(f"Unsupported format: {format}. Supported formats: toml, yaml")

    return config_path


def ensure_config_file(
    app_name: str,
    defaults: dict[str, Any] | None = None,
    format: Literal["toml", "yaml"] = "toml",
) -> Path:
    """Ensure a global config file exists, creating it with defaults if needed.

    Checks if the standard global config file exists. If it doesn't exist,
    creates it with the provided defaults (or an empty dict if no defaults given).
    If it does exist, returns the path without modification.

    Args:
        app_name: The application name (used in directory and file names).
        defaults: Default configuration data to write if the file doesn't exist.
                 If None, an empty dict is used.
        format: The configuration file format. Supported values are "toml" (default)
                and "yaml".

    Returns:
        The Path to the configuration file (whether it was created or already existed).

    Examples:
        >>> from utilityhub_config import ensure_config_file
        >>> path = ensure_config_file("myapp", {"debug": False})
        >>> str(path)  # doctest: +ELLIPSIS
        '.../.config/myapp/myapp.toml'
    """
    config_path = get_config_path(app_name, format=format)

    if not config_path.exists():
        data = defaults if defaults is not None else {}
        write_config(app_name, data, format=format)

    return config_path
