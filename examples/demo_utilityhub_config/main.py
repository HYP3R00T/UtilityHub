"""Witty demo for nested metadata source tracking before publishing to PyPI.

Run from repository root:
    /workspaces/UtilityHub/.venv/bin/python examples/demo_utilityhub_config/main.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import BaseModel
from utilityhub_config import load_settings
from utilityhub_config.metadata import SettingsMetadata

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_PACKAGE_SRC = REPO_ROOT / "packages" / "utilityhub_config" / "src"
if LOCAL_PACKAGE_SRC.exists():
    sys.path.insert(0, str(LOCAL_PACKAGE_SRC))


class ModelConfig(BaseModel):
    backend: str = "auto"
    device: str = "cpu"


class InferenceConfig(BaseModel):
    despill_strength: float = 0.25


class AppConfig(BaseModel):
    app_name: str = "ezck"
    model: ModelConfig = ModelConfig()
    inference: InferenceConfig = InferenceConfig()


LINE_WIDTH = 72


def source_row(metadata: SettingsMetadata, path: str, value: object) -> str:
    src = metadata.get_source(path)
    if src is None:
        return f"{path:<26} {str(value):<12} source=None path=None"
    return f"{path:<26} {str(value):<12} source={src.source:<9} path={src.source_path}"


def print_summary(settings: AppConfig, metadata: SettingsMetadata) -> None:
    print("\nConfig truth table: who set what")
    print("-" * LINE_WIDTH)
    rows = [
        source_row(metadata, "model", settings.model.model_dump()),
        source_row(metadata, "model.backend", settings.model.backend),
        source_row(metadata, "model.device", settings.model.device),
        source_row(metadata, "inference", settings.inference.model_dump()),
        source_row(metadata, "inference.despill_strength", settings.inference.despill_strength),
    ]
    print("\n".join(rows))


def main() -> None:
    print("Nested Field Source Tracking Demo: Director's Cut")
    print("=" * LINE_WIDTH)
    print("Local package source is used so you can trust this before shipping to PyPI.")

    with TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        project_config = project_root / "ezck.yaml"
        project_config.write_text(
            """
model:
  backend: auto
  device: cpu
inference:
  despill_strength: 0.6
""".lstrip()
        )

        print("\nScene 1: project config sets sane defaults.")
        print(f"Loaded project file: {project_config}")

        os.environ["EZCK_MODEL__DEVICE"] = "cuda"
        try:
            print("Scene 2: env var barges in with EZCK_MODEL__DEVICE=cuda.")
            print("Scene 3: runtime override insists model.backend=onnx.")
            settings, metadata = load_settings(
                AppConfig,
                app_name="ezck",
                env_prefix="EZCK",
                cwd=project_root,
                overrides={"model": {"backend": "onnx"}},
            )
        finally:
            del os.environ["EZCK_MODEL__DEVICE"]

    print("\nPrecedence recap")
    print("1. project file (ezck.yaml) sets model.backend=auto, model.device=cpu, inference.despill_strength=0.6")
    print("2. env var EZCK_MODEL__DEVICE overrides model.device to cuda")
    print("3. runtime override sets model.backend to onnx")

    print_summary(settings, metadata)

    print("\nChecks you care about before release")
    print("- metadata.get_source('model.backend') => overrides")
    print("- metadata.get_source('model.device') => env from EZCK_MODEL__DEVICE")
    print("- metadata.get_source('inference.despill_strength') => project")
    print("\nVerdict: nested source tracking finally tells the truth.")


if __name__ == "__main__":
    main()
