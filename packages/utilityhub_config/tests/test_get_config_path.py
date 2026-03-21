from pathlib import Path

import pytest
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


class TestGetConfigPathErrorConditions:
    """Test error conditions and invalid inputs."""

    def test_format_invalid_type_allowed(self) -> None:
        """Invalid format parameter is allowed (no validation)."""
        # The function doesn't validate format at runtime
        result = get_config_path("myapp", format="invalid")  # type: ignore
        assert str(result).endswith(".invalid")

    def test_empty_app_name(self) -> None:
        """Empty app name is handled gracefully."""
        result = get_config_path("")
        # Should still create a valid path structure
        assert result.name == ".toml"
        assert ".config" in result.parts

    def test_app_name_with_spaces(self) -> None:
        """App names with spaces are preserved."""
        app_name = "my app"
        result = get_config_path(app_name)
        assert app_name in result.parts

    def test_app_name_with_special_chars(self) -> None:
        """App names with special characters are preserved."""
        app_name = "my-app_test.123"
        result = get_config_path(app_name)
        assert app_name in result.parts


class TestGetConfigPathParametrized:
    """Parametrized tests for different formats and app names."""

    @pytest.mark.parametrize(
        "format_name,extension",
        [
            ("toml", ".toml"),
            ("yaml", ".yaml"),
            ("json", ".json"),
        ],
    )
    def test_all_formats_parametrized(self, format_name: str, extension: str) -> None:
        """Test all supported formats with parametrization."""
        result = get_config_path("testapp", format=format_name)  # type: ignore
        assert result.suffix == extension
        assert result.name == f"testapp{extension}"

    @pytest.mark.parametrize(
        "app_name",
        [
            "simple",
            "with_underscores",
            "with-hyphens",
            "with.dots",
            "with123numbers",
            "MixedCase",
        ],
    )
    def test_various_app_names(self, app_name: str) -> None:
        """Test various app name patterns."""
        result = get_config_path(app_name)
        assert app_name in result.parts
        assert result.name == f"{app_name}.toml"
        assert result.parent.name == app_name


class TestGetConfigPathIntegration:
    """Integration tests for get_config_path with real filesystem operations."""

    def test_path_can_be_used_for_file_operations(self, tmp_path: Path, monkeypatch) -> None:
        """Returned path can be used for actual file operations."""
        # Mock Path.home() to return our temp directory
        fake_home = tmp_path / "fake_home"
        fake_home.mkdir()

        def mock_home():
            return fake_home

        monkeypatch.setattr(Path, "home", mock_home)

        # Get the config path (now uses fake_home)
        config_path = get_config_path("testapp")

        # Create parent directories
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a file at that path
        test_content = "test config content"
        config_path.write_text(test_content)

        # Verify the file was created
        assert config_path.exists()
        assert config_path.read_text() == test_content

    def test_multiple_apps_dont_conflict(self, tmp_path: Path) -> None:
        """Different app names produce different paths."""
        app1_path = get_config_path("app1")
        app2_path = get_config_path("app2")

        assert app1_path != app2_path
        assert "app1" in str(app1_path)
        assert "app2" in str(app2_path)

    def test_format_parameter_affects_extension_only(self) -> None:
        """Format parameter only changes file extension, not directory structure."""
        toml_path = get_config_path("myapp", format="toml")
        yaml_path = get_config_path("myapp", format="yaml")
        json_path = get_config_path("myapp", format="json")

        # Directory structure should be the same
        assert toml_path.parent == yaml_path.parent == json_path.parent

        # Only extensions should differ
        assert toml_path.suffix == ".toml"
        assert yaml_path.suffix == ".yaml"
        assert json_path.suffix == ".json"

        # Base names should be the same
        assert toml_path.stem == yaml_path.stem == json_path.stem == "myapp"


class TestGetConfigPathEdgeCases:
    """Edge case tests for get_config_path function."""

    def test_app_name_with_special_characters(self) -> None:
        """App names with special characters are handled correctly."""
        # Test with underscores
        path = get_config_path("my_app")
        assert "my_app" in str(path)

        # Test with hyphens
        path = get_config_path("my-app")
        assert "my-app" in str(path)

        # Test with numbers
        path = get_config_path("app123")
        assert "app123" in str(path)

    def test_app_name_case_preserved(self) -> None:
        """App name case is preserved in the path."""
        path = get_config_path("MyApp")
        assert "MyApp" in str(path)

        path_lower = get_config_path("myapp")
        assert "myapp" in str(path_lower)

        assert path != path_lower

    def test_empty_app_name_allowed(self) -> None:
        """Empty app name is allowed (though unusual)."""
        path = get_config_path("")
        assert isinstance(path, Path)
        # Path will be ~/.config//.toml (empty directory name)

    def test_whitespace_app_name_allowed(self) -> None:
        """Whitespace app name is allowed."""
        path = get_config_path("   ")
        assert isinstance(path, Path)

    def test_app_name_with_slashes_allowed(self) -> None:
        """App name containing slashes is allowed (creates nested paths)."""
        path = get_config_path("my/app")
        assert "my/app" in str(path)

    def test_invalid_format_allowed(self) -> None:
        """Invalid format is allowed (just uses the string as extension)."""
        path = get_config_path("myapp", format="invalid")  # type: ignore
        assert str(path).endswith(".invalid")

    def test_format_case_insensitive(self) -> None:
        """Format parameter is NOT case insensitive - case is preserved."""
        toml_lower = get_config_path("myapp", format="toml")
        toml_upper = get_config_path("myapp", format="TOML")  # type: ignore
        toml_mixed = get_config_path("myapp", format="Toml")  # type: ignore

        # They are NOT equal because case is preserved in the filename
        assert toml_lower != toml_upper != toml_mixed
        assert str(toml_lower).endswith(".toml")
        assert str(toml_upper).endswith(".TOML")
        assert str(toml_mixed).endswith(".Toml")

    def test_format_with_extra_whitespace_allowed(self) -> None:
        """Format with whitespace is allowed."""
        path = get_config_path("myapp", format=" toml ")  # type: ignore
        assert str(path).endswith(". toml ")


class TestGetConfigPathDoctests:
    """Test cases that mirror the doctests in the function docstring."""

    def test_doctest_example_1(self) -> None:
        """Test the first doctest example."""
        from utilityhub_config import get_config_path

        path = get_config_path("myapp")
        path_str = str(path)
        assert path_str.endswith("/.config/myapp/myapp.toml")

    def test_doctest_example_2(self) -> None:
        """Test the yaml format doctest example."""
        from utilityhub_config import get_config_path

        yaml_path = get_config_path("myapp", format="yaml")
        yaml_str = str(yaml_path)
        assert yaml_str.endswith("/.config/myapp/myapp.yaml")

    def test_doctest_example_3(self) -> None:
        """Test the json format doctest example."""
        from utilityhub_config import get_config_path

        json_path = get_config_path("myapp", format="json")
        json_str = str(json_path)
        assert json_str.endswith("/.config/myapp/myapp.json")
