"""utilityhub_config

Small, deterministic configuration loader for automation tools.
"""

from utilityhub_config.api import load_settings
from utilityhub_config.utils import (
    expand_and_validate_path,
    expand_path,
    expand_path_validator,
)

__all__: list[str] = [
    "load_settings",
    "expand_path",
    "expand_and_validate_path",
    "expand_path_validator",
]


def main() -> None:
    print("utilityhub-config: use `load_settings()` in your code")
