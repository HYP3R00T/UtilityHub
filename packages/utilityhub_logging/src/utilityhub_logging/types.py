from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class LogFormat(StrEnum):
    PLAIN = "plain"
    JSON = "json"


class LogPathConvention(StrEnum):
    PLATFORM = "platform"
    HOME_HIDDEN = "home_hidden"
    CWD = "cwd"


class ManagedHandlerKind(StrEnum):
    APP = "app"
    SCOPE = "scope"


@dataclass(frozen=True, slots=True)
class ManagedHandlerRecord:
    logger_name: str
    handler_name: str
    kind: ManagedHandlerKind
    file_path: Path | None = None
