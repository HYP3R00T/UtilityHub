from __future__ import annotations

import sys
from pathlib import Path

# Ensure the package's src/ directory is on sys.path so tests can import the local package
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from pydantic import BaseModel
from utilityhub_config import load_settings


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
