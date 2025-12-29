"""
Fun demo: `load_settings` with precedence order.

Copy this file and run it:
  python demo_utilityhub_config.py
"""

import os

from pydantic import BaseModel
from utilityhub_config import load_settings


class PartyConfig(BaseModel):
    """A hilarious party planner config."""

    party_name: str = "boring_afternoon_tea"
    vibe: str = "chill"
    snack: str = "plain_crackers"


def main() -> None:
    # 1) Defaults — the worst timeline
    print("🎉 Party Setup (boring defaults):")
    settings, metadata = load_settings(PartyConfig)
    print(f"   Name: {settings.party_name} | Vibe: {settings.vibe} | Snack: {settings.snack}")

    # 2) Env override — someone's feeling spicy 🌶️
    print("\n🌶️ Wait, there's an env var (SNACK=jalapeño_poppers):")
    os.environ["SNACK"] = "jalapeño_poppers"
    try:
        settings, metadata = load_settings(PartyConfig)
        print(f"   Name: {settings.party_name} | Vibe: {settings.vibe} | Snack: {settings.snack}")
    finally:
        del os.environ["SNACK"]

    # 3) Runtime override — the boss has spoken
    print("\n👑 Runtime override (party_name=champagne_soirée, vibe=lit):")
    settings, metadata = load_settings(PartyConfig, overrides={"party_name": "champagne_soirée", "vibe": "lit"})
    print(f"   Name: {settings.party_name} | Vibe: {settings.vibe} | Snack: {settings.snack}")

    print("\n✨ Precedence wins: defaults < env < runtime overrides!")


if __name__ == "__main__":
    main()
