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
        fields = getattr(model, "model_fields", None)
        if fields is not None:
            return list(fields.keys())
        return list(getattr(model, "__fields__", {}).keys())

    def _determine_app_name(self, model: type[BaseModel]) -> str:
        """Determine the app name from explicit arg, model default, or class name.

        Precedence: explicit app_name > model field default > model class name (lowercased).
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
        home = Path.home()
        cfg_dir = home / ".config" / app
        return [cfg_dir / f"{app}.toml", cfg_dir / f"{app}.yaml"]

    def _project_config_paths(self, app: str) -> list[Path]:
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
        merged: dict[str, Any] = dict(existing)
        for key, value in incoming.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge_dict(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _collect_nested_env(self, top_level_fields: set[str]) -> list[tuple[list[str], str, str]]:
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
        cursor: dict[str, Any] = target
        for part in path_parts[:-1]:
            existing = cursor.get(part)
            if not isinstance(existing, dict):
                existing = {}
                cursor[part] = existing
            cursor = existing
        cursor[path_parts[-1]] = value
