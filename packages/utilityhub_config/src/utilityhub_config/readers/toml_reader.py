from __future__ import annotations

from pathlib import Path
from typing import Any


def read_toml(path: Path) -> dict[str, Any]:
    """Read a TOML file and return its contents as a dictionary.

    Parses a TOML file using Python's built-in tomllib module. If the file
    does not exist, returns an empty dictionary instead of raising an error.

    Args:
        path: Path to the TOML file to read.

    Returns:
        A dictionary containing the parsed TOML data. Returns an empty dict
        if the file does not exist.

    Raises:
        RuntimeError: If the file exists but cannot be parsed as valid TOML.
    """
    if not path.exists():
        return {}
    try:
        import tomllib

        with path.open("rb") as fh:
            return tomllib.load(fh) or {}
    except Exception as exc:  # be explicit in errors upstream
        raise RuntimeError(f"Failed to parse TOML at {path}: {exc}") from exc
