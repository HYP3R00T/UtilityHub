from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FieldSource:
    source: str
    source_path: str | None
    raw_value: Any


@dataclass
class SettingsMetadata:
    per_field: dict[str, FieldSource]

    def get_source(self, field: str) -> FieldSource | None:
        if not field:
            return None

        direct = self.per_field.get(field)
        if direct is not None:
            return direct

        if "." not in field:
            return None

        parts = field.split(".")
        if any(not part for part in parts):
            return None

        # Fall back to the nearest known parent path.
        for index in range(len(parts) - 1, 0, -1):
            parent_path = ".".join(parts[:index])
            parent = self.per_field.get(parent_path)
            if parent is not None:
                return parent

        return None
