from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the package's src/ directory is on sys.path so tests can import the local package
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from pydantic import BaseModel, field_validator
from utilityhub_config import (
    expand_and_validate_path,
    expand_path,
    expand_path_validator,
    load_settings,
)


class AppDefaults(BaseModel):
    app_name: str = "utilityhub"
    log_level: str = "INFO"
    database_url: str = "sqlite:///memory"


def test_defaults_only(tmp_path: Path) -> None:
    settings, meta = load_settings(AppDefaults, cwd=tmp_path)
    assert settings.database_url == "sqlite:///memory"
    src = meta.get_source("database_url")
    assert src is not None and src.source == "defaults"


def test_env_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://user@localhost/db")

    class App(BaseModel):
        database_url: str

    settings, meta = load_settings(App, cwd=tmp_path)
    assert settings.database_url == "postgres://user@localhost/db"
    src = meta.get_source("database_url")
    assert src and src.source == "env"


def test_validation_error_shows_context(tmp_path: Path) -> None:
    class Req(BaseModel):
        database_url: str

    with pytest.raises(Exception) as exc:
        load_settings(Req, cwd=tmp_path)

    text = str(exc.value)
    assert "Validation errors" in text
    assert "Files checked" in text
    assert "Precedence" in text


def test_dotenv_override(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite:///from_dotenv")

    class App(BaseModel):
        database_url: str

    settings, meta = load_settings(App, cwd=tmp_path)
    assert settings.database_url == "sqlite:///from_dotenv"
    src = meta.get_source("database_url")
    assert src and src.source == "dotenv"


def test_project_toml(tmp_path: Path) -> None:
    cfg = tmp_path / "utilityhub.toml"
    cfg.write_text('database_url = "sqlite:///from_toml"\n')

    class App(BaseModel):
        app_name: str = "utilityhub"
        database_url: str

    settings, meta = load_settings(App, cwd=tmp_path)
    assert settings.database_url == "sqlite:///from_toml"
    src = meta.get_source("database_url")
    assert src and src.source == "project"


def test_expand_path_tilde(tmp_path: Path) -> None:
    """Test that tilde (~) expands to user home directory."""
    # Create a path with tilde
    path_with_tilde = "~/test_config.yaml"
    expanded = expand_path(path_with_tilde)

    # Should expand to home directory
    expected = Path.home() / "test_config.yaml"
    assert expanded == expected
    assert str(expanded).startswith(str(Path.home()))


def test_expand_path_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that environment variables ($VAR) are expanded."""
    monkeypatch.setenv("TEST_CONFIG_DIR", "/custom/config")

    path_with_var = "$TEST_CONFIG_DIR/app.yaml"
    expanded = expand_path(path_with_var)

    assert expanded == Path("/custom/config/app.yaml")


def test_expand_path_env_var_braces(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that environment variables (${VAR}) with braces are expanded."""
    monkeypatch.setenv("CONFIG_DIR", "/etc/config")

    path_with_var = "${CONFIG_DIR}/app.toml"
    expanded = expand_path(path_with_var)

    assert expanded == Path("/etc/config/app.toml")


def test_expand_path_combined_tilde_and_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that tilde and environment variables work together."""
    monkeypatch.setenv("SUBDIR", "myapp")

    path_with_both = "~/$SUBDIR/config.yaml"
    expanded = expand_path(path_with_both)

    expected = Path.home() / "myapp" / "config.yaml"
    assert expanded == expected


def test_expand_path_undefined_env_var() -> None:
    """Test that undefined environment variables are left as-is."""
    # os.path.expandvars doesn't raise error for undefined vars - it leaves them unchanged
    path_with_undefined = "$NONEXISTENT_VERY_UNIQUE_VAR_12345/config.yaml"

    result = expand_path(path_with_undefined)
    # The undefined variable should be left in the path
    assert str(result) == "$NONEXISTENT_VERY_UNIQUE_VAR_12345/config.yaml"


def test_expand_and_validate_path_existing(tmp_path: Path) -> None:
    """Test that expand_and_validate_path succeeds for existing paths."""
    # Create an actual file
    config_file = tmp_path / "existing_config.yaml"
    config_file.write_text("test: value")

    # Use an environment variable pointing to the file

    os.environ["TEST_CONFIG_FILE"] = str(config_file)
    path_with_var = "$TEST_CONFIG_FILE"

    result = expand_and_validate_path(path_with_var)
    assert result == config_file
    assert result.exists()


def test_expand_and_validate_path_nonexistent() -> None:
    """Test that expand_and_validate_path raises FileNotFoundError for missing paths."""
    nonexistent_path = "/very/unlikely/path/that/does/not/exist.yaml"

    with pytest.raises(FileNotFoundError):
        expand_and_validate_path(nonexistent_path)


def test_expand_and_validate_path_tilde_nonexistent() -> None:
    """Test validation error with tilde expansion."""
    # Even though ~ exists, the expanded path should not exist
    path_with_tilde = "~/very_unlikely_appconfig_xyz_12345.yaml"

    with pytest.raises(FileNotFoundError):
        expand_and_validate_path(path_with_tilde)


def test_expand_path_relative() -> None:
    """Test that relative paths are left as-is (no special expansion)."""
    relative_path = "config/app.yaml"
    expanded = expand_path(relative_path)

    # Relative paths should become absolute based on current working directory
    # But since no tilde or env vars, the result should be processable
    assert isinstance(expanded, Path)


def test_expand_path_absolute() -> None:
    """Test that absolute paths work correctly."""
    absolute_path = "/etc/config/app.yaml"
    expanded = expand_path(absolute_path)

    assert expanded == Path("/etc/config/app.yaml")
    assert expanded.is_absolute()


def test_pydantic_validator_with_path_expansion(tmp_path: Path) -> None:
    """Test using expand_path_validator in a Pydantic model."""
    # Create a config file
    config_file = tmp_path / "app.yaml"
    config_file.write_text("test: value")

    # Create a Pydantic model with path validator
    class ConfigModel(BaseModel):
        config_path: Path

        @field_validator("config_path", mode="before")
        @classmethod
        def validate_config_path(cls, v: Path | str) -> Path:
            return expand_path_validator(v)

    # Test with environment variable expansion

    os.environ["TEST_CONFIG_PATH"] = str(config_file)
    model = ConfigModel(config_path="$TEST_CONFIG_PATH")  # type: ignore[arg-type]

    assert isinstance(model.config_path, Path)
    assert model.config_path == config_file
    assert model.config_path.exists()


def test_pydantic_validator_missing_file(tmp_path: Path) -> None:
    """Test that validator raises error for missing files."""

    class ConfigModel(BaseModel):
        config_path: Path

        @field_validator("config_path", mode="before")
        @classmethod
        def validate_config_path(cls, v: Path | str) -> Path:
            return expand_path_validator(v)

    with pytest.raises(FileNotFoundError):
        ConfigModel(config_path="/nonexistent/file.yaml")  # type: ignore[arg-type]
