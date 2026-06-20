from __future__ import annotations

import os
from pathlib import Path

from utilityhub_logging.types import LogPathConvention


def resolve_logs_path(
    app_name: str,
    logs_path: str | os.PathLike[str] | None = None,
    *,
    default_convention: LogPathConvention | str = LogPathConvention.PLATFORM,
    create: bool = True,
) -> Path:
    if not app_name.strip():
        msg = "app_name must be a non-empty string"
        raise ValueError(msg)

    if logs_path is not None:
        path = Path(logs_path).expanduser()
    else:
        convention = LogPathConvention(default_convention)
        path = _resolve_default_logs_path(app_name=app_name, convention=convention)

    if create:
        path.mkdir(parents=True, exist_ok=True)

    return path


def _resolve_default_logs_path(app_name: str, *, convention: LogPathConvention) -> Path:
    if convention is LogPathConvention.CWD:
        return Path.cwd() / "logs" / app_name

    if convention is LogPathConvention.HOME_HIDDEN:
        return Path.home() / f".{app_name}" / "logs"

    if os.name == "nt":
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / app_name / "Logs"
        return Path.home() / "AppData" / "Local" / app_name / "Logs"

    if os.sys.platform == "darwin":
        return Path.home() / "Library" / "Logs" / app_name

    return Path.home() / ".local" / "state" / app_name / "logs"
