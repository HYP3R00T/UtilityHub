"""Tests for write_config and ensure_config_file utility functions."""

from pathlib import Path

import pytest
import yaml
from pydantic import BaseModel
from utilityhub_config import ensure_config_file, write_config
from utilityhub_config.readers import read_toml


class DemoConfig(BaseModel):
    """Simple config model used for writer utility tests."""

    database_url: str = "sqlite:///default.db"
    debug: bool = False
    workers: int = 4


class PathConfig(BaseModel):
    """Config model with Path fields for serialization regression tests."""

    model_path: Path = Path("~/.config/myapp/model.pth")
    cache_dir: Path = Path("~/.cache/myapp")


class TestWriteConfig:
    """Test the write_config function."""

    def test_write_config_creates_directory(self, tmp_path: Path, monkeypatch) -> None:
        """write_config creates the config directory if it doesn't exist."""
        # Mock Path.home() to use tmp_path
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        config = DemoConfig()
        result_path = write_config(config, "testapp")

        # Check that directory was created
        assert result_path.parent.exists()
        assert result_path.parent.name == "testapp"
        assert result_path.parent.parent.name == ".config"

    def test_write_config_toml_format(self, tmp_path: Path, monkeypatch) -> None:
        """write_config writes TOML format correctly."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        config = DemoConfig(database_url="sqlite:///test.db", debug=True)
        result_path = write_config(config, "testapp", format="toml")

        assert result_path.exists()
        assert result_path.suffix == ".toml"

        # Read back and verify content
        data = read_toml(result_path)
        assert data == config.model_dump(mode="json")

    def test_write_config_yaml_format(self, tmp_path: Path, monkeypatch) -> None:
        """write_config writes YAML format correctly."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        config = DemoConfig(database_url="sqlite:///test.db", debug=True)
        result_path = write_config(config, "testapp", format="yaml")

        assert result_path.exists()
        assert result_path.suffix == ".yaml"

        # Read back and verify content
        with result_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data == config.model_dump(mode="json")

    def test_write_config_returns_correct_path(self, tmp_path: Path, monkeypatch) -> None:
        """write_config returns the correct config file path."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        result_path = write_config(DemoConfig(), "myapp")

        expected_path = fake_home / ".config" / "myapp" / "myapp.toml"
        assert result_path == expected_path

    def test_write_config_overwrites_existing_file(self, tmp_path: Path, monkeypatch) -> None:
        """write_config overwrites existing config files."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        config_path = fake_home / ".config" / "myapp" / "myapp.toml"
        config_path.parent.mkdir(parents=True)

        # Create existing file with different content
        config_path.write_text('old = "content"')

        # Write new content
        config = DemoConfig(database_url="sqlite:///new.db", workers=8)
        result_path = write_config(config, "myapp")

        # Verify it was overwritten
        data = read_toml(result_path)
        assert data == config.model_dump(mode="json")

    def test_write_config_invalid_format_raises_error(self, tmp_path: Path, monkeypatch) -> None:
        """write_config raises ValueError for invalid format."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        with pytest.raises(ValueError, match="Unsupported format"):
            write_config(DemoConfig(), "myapp", format="invalid")  # type: ignore[arg-type]

    def test_write_config_json_format_raises_error(self, tmp_path: Path, monkeypatch) -> None:
        """write_config rejects json as an unsupported output format."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        with pytest.raises(ValueError, match="Unsupported format"):
            write_config(DemoConfig(), "myapp", format="json")  # type: ignore[arg-type]

    def test_write_config_uses_explicit_path(self, tmp_path: Path) -> None:
        """write_config writes to explicit path when provided."""
        output_path = tmp_path / "custom" / "settings.toml"
        config = DemoConfig(debug=True)

        result_path = write_config(config, "ignored-app", path=output_path)

        assert result_path == output_path
        assert result_path.exists()
        assert read_toml(result_path) == config.model_dump(mode="json")

    def test_write_config_yaml_path_fields_are_portable(self, tmp_path: Path) -> None:
        """YAML output stores Path values as scalars without Python tags."""
        output_path = tmp_path / "config" / "settings.yaml"

        result_path = write_config(PathConfig(), "myapp", path=output_path, format="yaml")

        assert result_path == output_path
        with result_path.open("r", encoding="utf-8") as handle:
            text = handle.read()
        assert "!!python/object" not in text

        with result_path.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle)
        assert loaded == PathConfig().model_dump(mode="json")

    def test_write_config_toml_path_fields_roundtrip(self, tmp_path: Path) -> None:
        """TOML output supports Path fields by serializing to plain strings."""
        output_path = tmp_path / "config" / "settings.toml"

        result_path = write_config(PathConfig(), "myapp", path=output_path, format="toml")

        assert result_path == output_path
        loaded = read_toml(result_path)
        assert loaded == PathConfig().model_dump(mode="json")
        validated = PathConfig.model_validate(loaded)
        assert validated == PathConfig()


class TestEnsureConfigFile:
    """Test the ensure_config_file function."""

    def test_ensure_config_file_creates_missing_file(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file creates a config file if it doesn't exist."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        config = DemoConfig(database_url="sqlite:///first-run.db", workers=2)
        result_path = ensure_config_file(config, "testapp")

        assert result_path.exists()
        assert result_path.suffix == ".toml"

        # Verify content
        data = read_toml(result_path)
        assert data == config.model_dump(mode="json")

    def test_ensure_config_file_returns_existing_file_path(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file returns path to existing file without modification."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        # Create file first
        config_path = fake_home / ".config" / "myapp" / "myapp.toml"
        config_path.parent.mkdir(parents=True)
        existing_data = {"existing": "data"}
        import tomli_w

        with config_path.open("wb") as f:
            tomli_w.dump(existing_data, f)

        # Call ensure_config_file
        result_path = ensure_config_file(DemoConfig(), "myapp")

        assert result_path == config_path
        assert result_path.exists()

        # Verify content wasn't changed
        data = read_toml(result_path)
        assert data == existing_data

    def test_ensure_config_file_creates_file_from_instance(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file creates file from instance values when missing."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        config = DemoConfig(debug=True, workers=16)
        result_path = ensure_config_file(config, "testapp")

        assert result_path.exists()

        # Verify content matches the serialized instance
        data = read_toml(result_path)
        assert data == config.model_dump(mode="json")

    def test_ensure_config_file_uses_correct_format(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file uses the specified format."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        config = DemoConfig(debug=True)
        result_path = ensure_config_file(config, "testapp", format="yaml")

        assert result_path.suffix == ".yaml"
        assert result_path.exists()

        # Verify it's valid YAML
        with result_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data == config.model_dump(mode="json")

    def test_ensure_config_file_returns_correct_path(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file returns the correct config file path."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        result_path = ensure_config_file(DemoConfig(), "myapp")

        expected_path = fake_home / ".config" / "myapp" / "myapp.toml"
        assert result_path == expected_path

    def test_ensure_config_file_uses_explicit_path(self, tmp_path: Path) -> None:
        """ensure_config_file writes to explicit path when file is missing."""
        output_path = tmp_path / "custom" / "bootstrap.yaml"
        config = DemoConfig(debug=True)

        result_path = ensure_config_file(config, "ignored-app", path=output_path, format="yaml")

        assert result_path == output_path
        assert result_path.exists()
        with output_path.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle)
        assert loaded == config.model_dump(mode="json")


class TestWriteConfigEnsureConfigFileIntegration:
    """Integration tests for write_config and ensure_config_file working together."""

    def test_write_then_ensure_returns_existing(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file doesn't overwrite files created by write_config."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        # Write config first
        original = DemoConfig(database_url="sqlite:///original.db", workers=1)
        write_config(original, "testapp")

        # Ensure config file - should not change anything
        candidate = DemoConfig(database_url="sqlite:///candidate.db", workers=99)
        result_path = ensure_config_file(candidate, "testapp")

        # Verify original data is preserved
        data = read_toml(result_path)
        assert data == original.model_dump(mode="json")
