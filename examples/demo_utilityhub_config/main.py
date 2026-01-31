"""
Fun demo: `load_settings` with precedence order and explicit config files.

Copy this file and run it:
  python demo_utilityhub_config.py

Demonstrates:
  • Loading from defaults
  • Environment variable overrides
  • Runtime overrides
  • Loading from explicit YAML/TOML config files (NEW!)
  • Precedence order: defaults < env < config file < runtime overrides
"""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import BaseModel
from utilityhub_config import load_settings
from utilityhub_config.metadata import SettingsMetadata


class PartyConfig(BaseModel):
    """A hilariously detailed party planner config."""

    party_name: str = "boring_afternoon_tea"
    vibe: str = "chill"
    snack: str = "plain_crackers"


def print_settings(title: str, settings: PartyConfig, metadata: SettingsMetadata | None = None) -> None:
    """Pretty-print settings with a fun title."""
    print(f"\n{title}")
    print(f"   Name: {settings.party_name} | Vibe: {settings.vibe} | Snack: {settings.snack}")
    if metadata:
        # Show sources for each field
        print("   Sources:")
        for field_name in ["party_name", "vibe", "snack"]:
            source = metadata.get_source(field_name)
            if source:
                print(f"     - {field_name}: {source.source} ({source.source_path})")


def main() -> None:
    print("=" * 70)
    print("🎉 UTILITYHUB_CONFIG DEMO: The Ultimate Party Planning Journey 🎉")
    print("=" * 70)

    # 1) Defaults — the worst timeline
    print("\n1️⃣  Defaults (boring, sad timeline):")
    settings, metadata = load_settings(PartyConfig)
    print_settings("", settings)

    # 2) Env override — someone's feeling spicy 🌶️
    print("\n2️⃣  Environment Variable Override (SNACK=jalapeño_poppers):")
    os.environ["SNACK"] = "jalapeño_poppers"
    try:
        settings, metadata = load_settings(PartyConfig)
        print_settings("", settings)
    finally:
        del os.environ["SNACK"]

    # 3) Runtime override — the boss has spoken
    print("\n3️⃣  Runtime Override (party_name=champagne_soirée, vibe=lit):")
    settings, metadata = load_settings(PartyConfig, overrides={"party_name": "champagne_soirée", "vibe": "lit"})
    print_settings("", settings)

    # 4) NEW: Explicit config file (YAML)
    print("\n4️⃣  Loading from Explicit YAML Config File 🎯")
    with TemporaryDirectory() as tmpdir:
        yaml_config = Path(tmpdir) / "party_settings.yaml"
        yaml_config.write_text(
            """
party_name: beach_bash
vibe: chaotic
snack: piña_colada
"""
        )
        settings, metadata = load_settings(PartyConfig, config_file=yaml_config)
        print_settings(f"   (Loading from {yaml_config.name})", settings, metadata)

    # 5) NEW: Explicit config file (TOML)
    print("\n5️⃣  Loading from Explicit TOML Config File 🎯")
    with TemporaryDirectory() as tmpdir:
        toml_config = Path(tmpdir) / "party_settings.toml"
        toml_config.write_text(
            """
party_name = "garden_party"
vibe = "sophisticated"
snack = "cucumber_sandwiches"
"""
        )
        settings, metadata = load_settings(PartyConfig, config_file=toml_config)
        print_settings(f"   (Loading from {toml_config.name})", settings, metadata)

    # 6) NEW: Config file + env override (env wins!)
    print("\n6️⃣  Config File + Environment Override (env takes precedence!):")
    with TemporaryDirectory() as tmpdir:
        yaml_config = Path(tmpdir) / "party_settings.yaml"
        yaml_config.write_text(
            """
party_name: rave_party
vibe: electric
snack: energy_drink
"""
        )
        os.environ["VIBE"] = "nostalgic"
        try:
            settings, metadata = load_settings(PartyConfig, config_file=yaml_config)
            print_settings("", settings, metadata)
            print("   → Notice: VIBE from env (nostalgic) beats config file (electric)!")
        finally:
            del os.environ["VIBE"]

    # 7) NEW: Config file + runtime override (runtime wins!)
    print("\n7️⃣  Config File + Runtime Override (runtime takes the crown!):")
    with TemporaryDirectory() as tmpdir:
        yaml_config = Path(tmpdir) / "party_settings.yaml"
        yaml_config.write_text(
            """
party_name: corporate_mixer
vibe: awkward
snack: stale_pretzels
"""
        )
        settings, metadata = load_settings(
            PartyConfig,
            config_file=yaml_config,
            overrides={"snack": "lobster_thermidor"},
        )
        print_settings("", settings, metadata)
        print("   → Notice: snack from overrides (lobster_thermidor) beats config file (stale_pretzels)!")

    # Final summary
    print("\n" + "=" * 70)
    print("✨ PRECEDENCE ORDER VICTORY ROYALE ✨")
    print("=" * 70)
    print("""
defaults (worst)
    ↓
environment variables 🌍
    ↓
config files (YAML/TOML) 🎯
    ↓
runtime overrides (best!) 👑

Use this knowledge wisely. With great precedence comes great responsibility.
    """)


if __name__ == "__main__":
    main()
