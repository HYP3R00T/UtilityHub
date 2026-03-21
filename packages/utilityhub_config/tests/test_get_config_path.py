from __future__ import annotations

import sys
from pathlib import Path

# Ensure the package's src/ directory is on sys.path so tests can import the local package
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utilityhub_config import get_config_path


class TestGetConfigPathBasics:
    """Basic functionality tests for get_config_path()."""

    def test_get_config_path_returns_path(self) -> None:
        """get_config_path() returns a Path object."""
        result = get_config_path("myapp")
        assert isinstance(result, Path)

    def test_get_config_path_default_format_toml(self) -> None:
        """Default format parameter is 'toml'."""
        result = get_config_path("myapp")
        assert str(result).endswith("myapp.toml")

    def test_get_config_path_toml_format_explicit(self) -> None:
        """Explicit format='toml' returns TOML path."""
        result = get_config_path("myapp", format="toml")
        assert str(result).endswith("myapp.toml")

    def test_get_config_path_yaml_format(self) -> None:
        """format='yaml' returns YAML path."""
        result = get_config_path("myapp", format="yaml")
        assert str(result).endswith("myapp.yaml")

    def test_get_config_path_json_format(self) -> None:
        """format='json' returns JSON path."""
        result = get_config_path("myapp", format="json")
        assert str(result).endswith("myapp.json")


class TestGetConfigPathStructure:
    """Path structure validation tests."""

    def test_path_structure_contains_config_dir(self) -> None:
        """Path includes .config/{app_name} directory structure."""
        result = get_config_path("myapp")
        path_parts = result.parts
        assert ".config" in path_parts
        assert "myapp" in path_parts

    def test_path_structure_correct_order(self) -> None:
        """Path components are in correct order: home/.config/app_name/app_name.ext."""
        result = get_config_path("myapp")
        # Verify the last two components are correct
        assert result.name == "myapp.toml"
        assert result.parent.name == "myapp"
        assert result.parent.parent.name == ".config"

    def test_path_starts_with_home_directory(self) -> None:
        """Path starts with home directory."""
        result = get_config_path("myapp")
        home = Path.home()
        assert result.is_relative_to(home)

    def test_path_consistency_across_calls(self) -> None:
        """Repeated calls with same arguments return identical paths."""
        path1 = get_config_path("myapp")
        path2 = get_config_path("myapp")
        assert path1 == path2

    def test_app_name_in_directory_and_file(self) -> None:
        """App name appears in both directory name and filename."""
        app_name = "testapp"
        result = get_config_path(app_name)
        assert app_name in result.parts  # In directory
        assert result.name.startswith(app_name)  # In filename


class TestGetConfigPathFormatVariations:
    """Test various format parameter combinations."""

    def test_all_supported_formats(self) -> None:
        """All documented formats are supported without errors."""
        formats = ("toml", "yaml", "json")
        for fmt in formats:
            result = get_config_path("myapp", format=fmt)
            assert isinstance(result, Path)
            assert f"myapp.{fmt}" in str(result)

    def test_format_parameter_affects_extension(self) -> None:
        """Format parameter correctly determines file extension."""
        toml_path = get_config_path("myapp", format="toml")
        yaml_path = get_config_path("myapp", format="yaml")
        json_path = get_config_path("myapp", format="json")

        assert toml_path.suffix == ".toml"
        assert yaml_path.suffix == ".yaml"
        assert json_path.suffix == ".json"

    def test_different_formats_same_directory(self) -> None:
        """Different formats point to same directory, different filenames."""
        toml_path = get_config_path("myapp", format="toml")
        yaml_path = get_config_path("myapp", format="yaml")

        assert toml_path.parent == yaml_path.parent
        assert toml_path.name != yaml_path.name


class TestGetConfigPathAppNames:
    """Test behavior with various app names."""

    def test_simple_app_name(self) -> None:
        """Simple alphanumeric app name works correctly."""
        result = get_config_path("myapp")
        assert "myapp" in result.name
        assert "myapp" in result.parts

    def test_app_name_with_underscores(self) -> None:
        """App name with underscores is preserved."""
        app_name = "my_app"
        result = get_config_path(app_name)
        assert app_name in result.parts

    def test_app_name_with_hyphens(self) -> None:
        """App name with hyphens is preserved."""
        app_name = "my-app"
        result = get_config_path(app_name)
        assert app_name in result.parts

    def test_different_app_names_different_paths(self) -> None:
        """Different app names produce different paths."""
        path1 = get_config_path("app1")
        path2 = get_config_path("app2")
        assert path1 != path2
        assert "app1" in path1.parts
        assert "app2" in path2.parts

    def test_app_name_case_sensitive(self) -> None:
        """App name case is preserved in paths."""
        path_lower = get_config_path("myapp")
        path_upper = get_config_path("MyApp")
        assert path_lower != path_upper
        assert "myapp" in path_lower.parts
        assert "MyApp" in path_upper.parts


class TestGetConfigPathEdgeCases:
    """Edge case and boundary condition tests."""

    def test_single_character_app_name(self) -> None:
        """Single character app name is supported."""
        result = get_config_path("a")
        assert result.name == "a.toml"

    def test_long_app_name(self) -> None:
        """Long app names are supported."""
        long_name = "a" * 100
        result = get_config_path(long_name)
        assert long_name in result.parts

    def test_app_name_with_numbers(self) -> None:
        """App names containing numbers are supported."""
        result = get_config_path("app123")
        assert "app123" in result.parts

    def test_app_name_with_dots(self) -> None:
        """App names with dots are supported."""
        result = get_config_path("my.app")
        assert "my.app" in result.parts

    def test_format_case_sensitive(self) -> None:
        """Format parameter is case-sensitive (lowercase expected)."""
        # The function signature uses lowercase literal values
        result = get_config_path("myapp", format="toml")
        assert str(result).endswith(".toml")


class TestGetConfigPathIntegration:
    """Integration tests with Path operations."""

    def test_path_operations_work(self) -> None:
        """Returned Path object supports standard pathlib operations."""
        result = get_config_path("myapp")
        # Test various pathlib methods
        assert result.suffix == ".toml"
        assert result.name == "myapp.toml"
        assert isinstance(result.parent, Path)
        assert isinstance(result.stem, str)

    def test_path_string_representation(self) -> None:
        """Path can be converted to string."""
        result = get_config_path("myapp")
        path_str = str(result)
        assert isinstance(path_str, str)
        assert "myapp" in path_str
        assert ".config" in path_str

    def test_path_absolute(self) -> None:
        """Returned path is absolute (not relative)."""
        result = get_config_path("myapp")
        assert result.is_absolute()

    def test_path_parts_accessible(self) -> None:
        """Path parts can be accessed and manipulated."""
        result = get_config_path("myapp")
        parts = result.parts
        assert len(parts) > 0
        assert ".config" in parts

    def test_parent_attributes_accessible(self) -> None:
        """Can navigate parent directories without errors."""
        result = get_config_path("myapp")
        parent = result.parent
        grandparent = parent.parent
        assert isinstance(parent, Path)
        assert isinstance(grandparent, Path)
