from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FieldSource:
    """Represents the source of a configuration field value.

    Tracks where a particular configuration value came from, including the
    source type (e.g., "env", "global", "defaults") and the original raw value.

    Attributes:
        source: The source type where this value was found (e.g., "defaults",
            "global", "project", "dotenv", "env", "overrides").
        source_path: Optional path or identifier for the source (e.g., file path,
            environment variable name, or None for defaults).
        raw_value: The original value as read from the source, before any
            type conversion or validation.
    """

    source: str
    source_path: str | None
    raw_value: Any


@dataclass
class SettingsMetadata:
    """Metadata about how configuration settings were resolved.

    Provides detailed information about where each configuration field value
    came from, enabling debugging and understanding of configuration precedence.

    Attributes:
        per_field: Dictionary mapping field names to their FieldSource information.
            Field names may include nested paths using dot notation (e.g., "db.host").
    """

    per_field: dict[str, FieldSource]

    def get_source(self, field: str) -> FieldSource | None:
        """Get the source information for a specific field.

        Searches for the field by exact name first, then falls back to parent
        paths if the field represents a nested value.

        Args:
            field: The field name to look up. Can be a simple field name or
                a dotted path for nested fields (e.g., "database.host").

        Returns:
            The FieldSource for the field if found, or None if the field
            is not tracked in the metadata.

        Examples:
            >>> metadata.get_source("debug")
            FieldSource(source='defaults', source_path=None, raw_value=False)

            >>> metadata.get_source("database.host")
            FieldSource(source='env', source_path='ENV:DATABASE_HOST', raw_value='localhost')
        """
        return self.per_field.get(field)
