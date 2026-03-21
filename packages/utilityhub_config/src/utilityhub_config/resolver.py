from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from utilityhub_config.errors import ConfigError
from utilityhub_config.metadata import FieldSource, SettingsMetadata
from utilityhub_config.readers import parse_dotenv, read_toml, read_yaml


@dataclass
class PrecedenceResolver:
    """Resolves configuration from multiple sources in precedence order.

    Attributes:
        app_name: Application name for config file lookup. If None, derived from model class name.
        cwd: Working directory for config file search (defaults: current working directory).
        env_prefix: Optional prefix for environment variable lookup (e.g., 'MYAPP_').
        config_file: Explicit config file path to load as project config. If provided, skips auto-discovery.
    """

    app_name: str | None = None
    cwd: Path = field(default_factory=Path.cwd)
    env_prefix: str | None = None
    config_file: Path | None = None

    def __post_init__(self) -> None:
        if self.cwd is None:
            self.cwd = Path.cwd()
        self.precedence_order = [
            "defaults",
            "global",
            "project",
            "dotenv",
            "env",
            "overrides",
        ]

    def resolve(
        self, *, model: type[BaseModel], overrides: dict[str, Any]
    ) -> tuple[dict[str, Any], SettingsMetadata, list[str]]:
        """Resolve configuration from all sources according to precedence order.

        Merges configuration values from all available sources (defaults, global config,
        project config, dotenv, environment variables, and runtime overrides) in the
        correct precedence order. Tracks metadata about where each field value came from.

        Args:
            model: The Pydantic model class to get field information from.
            overrides: Runtime override values that take highest precedence.

        Returns:
            A tuple of (merged_config, metadata, checked_files) where:
            - merged_config: The final merged configuration dictionary
            - metadata: SettingsMetadata with source information for each field
            - checked_files: List of file paths that were checked (whether they existed or not)
        """
        app = self._determine_app_name(model)

        checked_files: list[str] = []
        per_field: dict[str, FieldSource] = {}

        # 1. defaults from model
        merged: dict[str, Any] = {}
        defaults = self._model_defaults(model)
        merged.update(defaults)
        for k, v in defaults.items():
            per_field[k] = FieldSource("defaults", None, v)

        # 2. global config
        global_paths = self._global_config_paths(app)
        for p in global_paths:
            checked_files.append(str(p))
            if p.exists():
                data = read_toml(p) if p.suffix.lower() == ".toml" else read_yaml(p)
                self._merge_into(merged, per_field, data, source_name="global", source_path=str(p))

        # 3. project config (explicit file or auto-discovery)
        if self.config_file is not None:
            # Explicit config_file provided: validate and load it
            checked_files.append(str(self.config_file))
            if not self.config_file.exists():
                raise ConfigError(f"Config file not found: {self.config_file}")
            if not self.config_file.is_file():
                raise ConfigError(f"Config file path is not a file: {self.config_file}")

            # Detect format from file extension
            suffix = self.config_file.suffix.lower()
            if suffix in {".yaml", ".yml"}:
                data = read_yaml(self.config_file)
            elif suffix == ".toml":
                data = read_toml(self.config_file)
            else:
                raise ConfigError(f"Unsupported config file format: {suffix}. Supported formats: .yaml, .yml, .toml")

            self._merge_into(merged, per_field, data, source_name="project", source_path=str(self.config_file))
        else:
            # No explicit file: use auto-discovery
            project_files = self._project_config_paths(app)
            for p in project_files:
                checked_files.append(str(p))
                if p.exists():
                    data = read_toml(p) if p.suffix.lower() == ".toml" else read_yaml(p)
                    self._merge_into(merged, per_field, data, source_name="project", source_path=str(p))

        # 4. dotenv
        dotenv_path = self.cwd / ".env"
        checked_files.append(str(dotenv_path))
        dotenv_data = parse_dotenv(dotenv_path)
        # dotenv keys are usually uppercase; normalize to field names
        normalized_dotenv = {self._normalize(k): v for k, v in dotenv_data.items()}
        self._merge_into(merged, per_field, normalized_dotenv, source_name="dotenv", source_path=str(dotenv_path))

        # 5. environment variables
        env_map: dict[str, Any] = {}
        env_sources: dict[str, FieldSource] = {}
        for field_name in self._field_names(model):
            candidates: list[str] = []
            if self.env_prefix:
                candidates.append(f"{self.env_prefix}_{field_name.upper()}")
            candidates.append(field_name.upper())
            for name in candidates:
                if name in os.environ:
                    env_map[field_name] = os.environ[name]
                    env_sources[field_name] = FieldSource("env", f"ENV:{name}", os.environ[name])
                    break

        top_level_fields = set(self._field_names(model))
        nested_env = self._collect_nested_env(top_level_fields)
        for path_parts, env_name, env_value in nested_env:
            self._set_nested_value(env_map, path_parts, env_value)
            field_path = ".".join(path_parts)
            env_sources[field_path] = FieldSource("env", f"ENV:{env_name}", env_value)

        self._merge_into(merged, per_field, env_map, source_name="env")
        per_field.update(env_sources)

        # 6. overrides
        if overrides:
            self._merge_into(merged, per_field, overrides, source_name="overrides", source_path="runtime")

        metadata = SettingsMetadata(per_field=per_field)
        return merged, metadata, checked_files

    def _model_defaults(self, model: type[BaseModel]) -> dict[str, Any]:
        """Extract default values from a Pydantic model.

        Gets the default values defined in the model's fields, supporting both
        Pydantic v1 and v2 syntax.

        Args:
            model: The Pydantic model class to extract defaults from.

        Returns:
            Dictionary mapping field names to their default values.
        """
        out: dict[str, Any] = {}
        # pydantic v2
        fields = getattr(model, "model_fields", None)
        if fields is not None:
            for k, info in fields.items():
                if getattr(info, "default", None) not in (None, ...):
                    out[k] = info.default
        else:
            # pydantic v1 style
            fields = getattr(model, "__fields__", {})
            for k, f in fields.items():
                if f.default is not None:
                    out[k] = f.default
        return out

    def _field_names(self, model: type[BaseModel]) -> list[str]:
        """Get the field names from a Pydantic model.

        Extracts field names from the model, supporting both Pydantic v1 and v2 syntax.

        Args:
            model: The Pydantic model class to get field names from.

        Returns:
            List of field names defined in the model.
        """
        fields = getattr(model, "model_fields", None)
        if fields is not None:
            return list(fields.keys())
        return list(getattr(model, "__fields__", {}).keys())

    def _determine_app_name(self, model: type[BaseModel]) -> str:
        """Determine the application name from various sources.

        Determines the app name in this precedence order:
        1. Explicitly provided app_name parameter
        2. Default value of 'app_name' field in the model
        3. Model class name (lowercased)

        Args:
            model: The Pydantic model class to determine app name for.

        Returns:
            The determined application name as a string.
        """
        if self.app_name:
            return self.app_name
        # try to pull default from model field 'app_name' if present
        fields = getattr(model, "model_fields", None)
        if fields and "app_name" in fields:
            default = fields["app_name"].default
            if default not in (None, ...):
                return str(default)
        # fallback to model class name
        return model.__name__.lower()

    def _global_config_paths(self, app: str) -> list[Path]:
        """Get the standard global configuration file paths for an app.

        Returns the XDG Base Directory standard paths for global configuration:
        ~/.config/{app}/{app}.toml and ~/.config/{app}/{app}.yaml

        Args:
            app: The application name.

        Returns:
            List of Path objects for potential global config files.
        """
        home = Path.home()
        cfg_dir = home / ".config" / app
        return [cfg_dir / f"{app}.toml", cfg_dir / f"{app}.yaml"]

    def _project_config_paths(self, app: str) -> list[Path]:
        """Get potential project configuration file paths.

        Searches for configuration files in the current working directory and
        config/ subdirectory. Looks for both TOML and YAML files.

        Args:
            app: The application name used in filename patterns.

        Returns:
            List of Path objects for potential project config files, in search order.
        """
        out: list[Path] = []
        root_toml = self.cwd / f"{app}.toml"
        root_yaml = self.cwd / f"{app}.yaml"
        out.extend([root_toml, root_yaml])
        config_dir = self.cwd / "config"
        if config_dir.exists() and config_dir.is_dir():
            for ext in ("*.toml", "*.yaml", "*.yml"):
                out.extend(sorted(config_dir.glob(ext)))
        return out

    def _normalize(self, key: str) -> str:
        """Normalize a configuration key for consistent field matching.

        Converts keys to lowercase, replaces hyphens with underscores, and strips whitespace.

        Args:
            key: The raw key string to normalize.

        Returns:
            The normalized key string.
        """
        return key.strip().lower().replace("-", "_")

    def _merge_into(
        self,
        target: dict[str, Any],
        per_field: dict[str, FieldSource],
        source: dict[str, Any],
        *,
        source_name: str,
        source_path: str | None = None,
    ) -> None:
        """Merge configuration values from a source into the target dictionary.

        Merges values from a configuration source into the target config dict,
        handling nested dictionaries and recording metadata about field sources.

        Args:
            target: The target configuration dictionary to merge into.
            per_field: Dictionary to record FieldSource metadata for each field.
            source: The source configuration dictionary to merge from.
            source_name: Name of the source (e.g., "global", "env").
            source_path: Optional path/identifier for the source.
        """
        # source keys may be in various forms; normalize and map to fields
        for k, v in source.items():
            nk = self._normalize(str(k))
            existing = target.get(nk)
            if isinstance(existing, dict) and isinstance(v, dict):
                target[nk] = self._deep_merge_dict(existing, v)
            else:
                target[nk] = v
            per_field[nk] = FieldSource(source_name, source_path, v)
            self._record_nested_sources(per_field, nk, v, source_name=source_name, source_path=source_path)

    def _record_nested_sources(
        self,
        per_field: dict[str, FieldSource],
        parent_path: str,
        value: Any,
        *,
        source_name: str,
        source_path: str | None,
    ) -> None:
        """Record source information for nested configuration values.

        Recursively walks through nested dictionaries and BaseModel instances
        to record FieldSource metadata for all nested fields.

        Args:
            per_field: Dictionary to record FieldSource metadata for each field.
            parent_path: The dotted path to the parent field (e.g., "database").
            value: The value to inspect for nested fields.
            source_name: Name of the source for these nested fields.
            source_path: Optional path/identifier for the source.
        """
        if isinstance(value, BaseModel):
            nested = value.model_dump(mode="python")
        elif isinstance(value, dict):
            nested = value
        else:
            return

        for child_key, child_value in nested.items():
            child_path = f"{parent_path}.{self._normalize(str(child_key))}"
            per_field[child_path] = FieldSource(source_name, source_path, child_value)
            self._record_nested_sources(
                per_field,
                child_path,
                child_value,
                source_name=source_name,
                source_path=source_path,
            )

    def _deep_merge_dict(self, existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries, preserving nested structure.

        Recursively merges the incoming dictionary into the existing one.
        When both dictionaries have the same key with dict values, they are
        merged recursively rather than the incoming value replacing the existing one.

        Args:
            existing: The existing dictionary to merge into.
            incoming: The incoming dictionary to merge from.

        Returns:
            A new dictionary with the merged result.
        """
        merged: dict[str, Any] = dict(existing)
        for key, value in incoming.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge_dict(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _collect_nested_env(self, top_level_fields: set[str]) -> list[tuple[list[str], str, str]]:
        """Collect nested environment variables for configuration.

        Parses environment variables that represent nested configuration paths
        using double underscores (e.g., DATABASE__HOST=localhost).
        Handles both prefixed and unprefixed environment variables.

        Args:
            top_level_fields: Set of valid top-level field names.

        Returns:
            List of tuples (path_parts, env_name, env_value) for nested env vars.
        """
        candidates: dict[tuple[str, ...], tuple[list[str], str, str, int]] = {}
        prefix = f"{self.env_prefix}_".upper() if self.env_prefix else None

        for env_name, env_value in os.environ.items():
            keys_to_try: list[tuple[str, int]] = [(env_name, 1)]
            if prefix and env_name.startswith(prefix):
                keys_to_try.insert(0, (env_name[len(prefix) :], 2))

            for candidate, priority in keys_to_try:
                if "__" not in candidate:
                    continue
                raw_parts = candidate.split("__")
                if any(not part for part in raw_parts):
                    continue
                parts = [self._normalize(part) for part in raw_parts]
                if parts[0] not in top_level_fields:
                    continue

                key = tuple(parts)
                current = candidates.get(key)
                if current is None or priority > current[3]:
                    candidates[key] = (parts, env_name, env_value, priority)

        return [(parts, env_name, env_value) for parts, env_name, env_value, _ in candidates.values()]

    def _set_nested_value(self, target: dict[str, Any], path_parts: list[str], value: Any) -> None:
        """Set a value at a nested path in a dictionary.

        Creates intermediate dictionaries as needed to set a value at a deeply
        nested path specified by path_parts.

        Args:
            target: The root dictionary to modify.
            path_parts: List of path components (e.g., ["database", "host"]).
            value: The value to set at the nested path.
        """
        cursor: dict[str, Any] = target
        for part in path_parts[:-1]:
            existing = cursor.get(part)
            if not isinstance(existing, dict):
                existing = {}
                cursor[part] = existing
            cursor = existing
        cursor[path_parts[-1]] = value
