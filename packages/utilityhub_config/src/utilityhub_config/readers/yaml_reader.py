from __future__ import annotations

from pathlib import Path
from typing import Any


def read_yaml(path: Path) -> dict[str, Any]:
    """Read a YAML file and return its contents as a dictionary.

    Parses a YAML file using PyYAML's safe_load function. If the file does not exist,
    returns an empty dictionary instead of raising an error.

    Args:
        path: Path to the YAML file to read.

    Returns:
        A dictionary containing the parsed YAML data. Returns an empty dict
        if the file does not exist.

    Raises:
        RuntimeError: If PyYAML is not installed, or if the file exists but
            cannot be parsed as valid YAML.
    """
    if not path.exists():
        return {}
    try:
        import yaml

        with path.open("r", encoding="utf8") as fh:
            return yaml.safe_load(fh) or {}
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"YAML file found at {path}, but PyYAML is not installed. Install 'PyYAML' to enable YAML support."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to parse YAML at {path}: {exc}") from exc
