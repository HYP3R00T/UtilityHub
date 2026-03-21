"""Tests for write_config and ensure_config_file utility functions."""

from pathlib import Path

import pytest
import yaml
from utilityhub_config import ensure_config_file, write_config
from utilityhub_config.readers import read_toml


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

        config_data = {"test": "value"}
        result_path = write_config("testapp", config_data)

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

        config_data = {"database": {"url": "sqlite:///test.db"}, "debug": True}
        result_path = write_config("testapp", config_data, format="toml")

        assert result_path.exists()
        assert result_path.suffix == ".toml"

        # Read back and verify content
        data = read_toml(result_path)
        assert data == config_data

    def test_write_config_yaml_format(self, tmp_path: Path, monkeypatch) -> None:
        """write_config writes YAML format correctly."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        config_data = {"database": {"url": "sqlite:///test.db"}, "debug": True}
        result_path = write_config("testapp", config_data, format="yaml")

        assert result_path.exists()
        assert result_path.suffix == ".yaml"

        # Read back and verify content
        with result_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data == config_data

    def test_write_config_returns_correct_path(self, tmp_path: Path, monkeypatch) -> None:
        """write_config returns the correct config file path."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        result_path = write_config("myapp", {"test": "data"})

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
        new_data = {"new": "content"}
        result_path = write_config("myapp", new_data)

        # Verify it was overwritten
        data = read_toml(result_path)
        assert data == new_data

    def test_write_config_invalid_format_raises_error(self, tmp_path: Path, monkeypatch) -> None:
        """write_config raises ValueError for invalid format."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        with pytest.raises(ValueError, match="Unsupported format"):
            write_config("myapp", {"test": "data"}, format="invalid")  # type: ignore


class TestEnsureConfigFile:
    """Test the ensure_config_file function."""

    def test_ensure_config_file_creates_missing_file(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file creates a config file if it doesn't exist."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        defaults = {"database": {"url": "sqlite:///default.db"}}
        result_path = ensure_config_file("testapp", defaults=defaults)

        assert result_path.exists()
        assert result_path.suffix == ".toml"

        # Verify content
        data = read_toml(result_path)
        assert data == defaults

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
        result_path = ensure_config_file("myapp")

        assert result_path == config_path
        assert result_path.exists()

        # Verify content wasn't changed
        data = read_toml(result_path)
        assert data == existing_data

    def test_ensure_config_file_creates_empty_file_when_no_defaults(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file creates empty config file when no defaults provided."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        result_path = ensure_config_file("testapp")

        assert result_path.exists()

        # Verify it's empty (just a TOML table)
        data = read_toml(result_path)
        assert data == {}

    def test_ensure_config_file_uses_correct_format(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file uses the specified format."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        result_path = ensure_config_file("testapp", format="yaml")

        assert result_path.suffix == ".yaml"
        assert result_path.exists()

        # Verify it's valid YAML
        with result_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data == {}

    def test_ensure_config_file_returns_correct_path(self, tmp_path: Path, monkeypatch) -> None:
        """ensure_config_file returns the correct config file path."""
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        result_path = ensure_config_file("myapp")

        expected_path = fake_home / ".config" / "myapp" / "myapp.toml"
        assert result_path == expected_path


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
        original_data = {"original": "data"}
        write_config("testapp", original_data)

        # Ensure config file - should not change anything
        result_path = ensure_config_file("testapp", defaults={"should": "not be used"})

        # Verify original data is preserved
        data = read_toml(result_path)
        assert data == original_data
