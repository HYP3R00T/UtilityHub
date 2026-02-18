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

from pydantic import BaseModel, field_validator
from utilityhub_config import expand_path_validator, load_settings
from utilityhub_config.metadata import SettingsMetadata


class PartyConfig(BaseModel):
    """A hilariously detailed party planner config."""

    party_name: str = "boring_afternoon_tea"
    vibe: str = "chill"
    snack: str = "plain_crackers"


class PartyWithPathsConfig(BaseModel):
    """Party config with file paths that support expansion."""

    party_name: str = "boring_afternoon_tea"
    vibe: str = "chill"
    snack: str = "plain_crackers"
    playlist_file: Path = Path("/tmp/default_playlist.m3u")
    photo_directory: Path = Path("/tmp/default_photos")

    @field_validator("playlist_file", "photo_directory", mode="before")
    @classmethod
    def expand_paths(cls, v: Path | str) -> Path:
        """Automatically expand ~ and environment variables in paths."""
        return expand_path_validator(v)


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
    print("\n1  Defaults (boring, sad timeline):")
    settings, metadata = load_settings(PartyConfig)
    print_settings("", settings)

    # 2) Env override — someone's feeling spicy 🌶️
    print("\n2  Environment Variable Override (SNACK=jalapeño_poppers):")
    os.environ["SNACK"] = "jalapeño_poppers"
    try:
        settings, metadata = load_settings(PartyConfig)
        print_settings("", settings)
    finally:
        del os.environ["SNACK"]

    # 3) Runtime override — the boss has spoken
    print("\n3  Runtime Override (party_name=champagne_soirée, vibe=lit):")
    settings, metadata = load_settings(PartyConfig, overrides={"party_name": "champagne_soirée", "vibe": "lit"})
    print_settings("", settings)

    # 4) NEW: Explicit config file (YAML)
    print("\n4  Loading from Explicit YAML Config File 🎯")
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
    print("\n5  Loading from Explicit TOML Config File 🎯")
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
    print("\n6  Config File + Environment Override (env takes precedence!):")
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
    print("\n7  Config File + Runtime Override (runtime takes the crown!):")
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

    # 8) NEW: Path expansion with tilde and environment variables 🎯
    print("\n8  Path Expansion: Tilde (~) and Environment Variables 🎯")
    with TemporaryDirectory() as tmpdir:
        # Create actual directories and files for demo
        playlist_dir = Path(tmpdir) / "party_files"
        playlist_dir.mkdir()
        playlist_file = playlist_dir / "party.m3u"
        playlist_file.write_text("# Dance Mix\n/path/to/song1.mp3\n/path/to/song2.mp3")

        photo_dir = playlist_dir / "photos"
        photo_dir.mkdir()

        yaml_config = Path(tmpdir) / "party_paths.yaml"
        yaml_config.write_text(f"""
party_name: festival_vibes
vibe: electric
snack: festival_food
playlist_file: {str(playlist_file)}
photo_directory: {str(photo_dir)}
""")

        settings, metadata = load_settings(PartyWithPathsConfig, config_file=yaml_config)
        print(f"   Config from: {yaml_config.name}")
        print(f"   Playlist file: {settings.playlist_file} (exists: {settings.playlist_file.exists()})")
        print(f"   Photo directory: {settings.photo_directory} (exists: {settings.photo_directory.exists()})")

    # 9) NEW: Path expansion with environment variables 🌍
    print("\n9  Path Expansion: Using Environment Variables 🌍")
    with TemporaryDirectory() as tmpdir:
        # Set up environment
        os.environ["PARTY_MUSIC_DIR"] = str(Path(tmpdir) / "music")
        os.environ["PARTY_PHOTO_DIR"] = str(Path(tmpdir) / "photos")
        Path(os.environ["PARTY_MUSIC_DIR"]).mkdir()
        Path(os.environ["PARTY_PHOTO_DIR"]).mkdir()

        # Create the playlist file so it exists
        playlist_file = Path(os.environ["PARTY_MUSIC_DIR"]) / "playlist.m3u"
        playlist_file.write_text("# Dance Mix\n/path/to/song1.mp3\n/path/to/song2.mp3")

        try:
            yaml_config = Path(tmpdir) / "party_env_paths.yaml"
            yaml_config.write_text("""
party_name: env_expanded_bash
vibe: experimental
snack: mystery_snack
playlist_file: $PARTY_MUSIC_DIR/playlist.m3u
photo_directory: ${PARTY_PHOTO_DIR}
""")

            settings, metadata = load_settings(PartyWithPathsConfig, config_file=yaml_config)
            print("   Config with environment variable expansion:")
            print("   Playlist file: $PARTY_MUSIC_DIR/playlist.m3u")
            print(f"   → Expands to: {settings.playlist_file}")
            print("   Photo directory: ${PARTY_PHOTO_DIR}")
            print(f"   → Expands to: {settings.photo_directory}")
        finally:
            del os.environ["PARTY_MUSIC_DIR"]
            del os.environ["PARTY_PHOTO_DIR"]

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

🎯 BONUS: Path Expansion with ~ and Environment Variables
   - Tilde (~) expands to your home directory
   - Environment variables ($VAR or ${VAR}) expand automatically
   - Perfect for cross-platform paths in config files!
    """)


if __name__ == "__main__":
    main()
