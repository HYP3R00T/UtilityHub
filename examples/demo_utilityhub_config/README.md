# Demo: utilityhub_config — quick example ⚡️

A tiny, runnable script that demonstrates `utilityhub_config` and precedence order (defaults → global → **explicit config file** → dotenv → env → runtime overrides).

Features showcased:
- Loading settings from defaults
- Environment variable overrides
- Runtime overrides
- **NEW:** Loading from explicit config files (YAML/TOML) with format auto-detection

## Quickstart ▶️

This README assumes you will copy the example script into a file on your machine and run it there (no repo clone required).

- Requirements: Python 3.14+

- Steps (copy the `main.py` contents into a file named `demo_utilityhub_config.py` and run it):

```bash
# create and activate a small virtual environment
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
# .\.venv\Scripts\Activate.ps1

# upgrade pip and install runtime deps from PyPI
pip install --upgrade pip
pip install pydantic utilityhub_config

# save the example as demo_utilityhub_config.py and run it
python demo_utilityhub_config.py
```


## What to expect

The script prints the resolved settings and the *source* for each field (e.g., `defaults`, `env`, `project`, or `overrides`). Example output:

```
🎉 Party Setup (boring defaults):
   Name: boring_afternoon_tea | Vibe: chill | Snack: plain_crackers

🌶️ Wait, there's an env var (SNACK=jalapeño_poppers):
   Name: boring_afternoon_tea | Vibe: chill | Snack: jalapeño_poppers

👑 Runtime override (party_name=champagne_soirée, vibe=lit):
   Name: champagne_soirée | Vibe: lit | Snack: plain_crackers

🎯 Loading from explicit YAML config file (party_settings.yaml):
   Name: beach_bash | Vibe: chaotic | Snack: piña_colada

🎯 Loading from explicit TOML config file (party_settings.toml):
   Name: garden_party | Vibe: sophisticated | Snack: cucumber_sandwiches

✨ Precedence wins: defaults < env < config file < runtime overrides!
```

## Notes

- This example is intentionally simple: it is a script, not a package. No installation is required to run it.
- The script creates temporary config files (YAML and TOML) in the system temp directory to demonstrate the `config_file` parameter.
- If you prefer an installable example, I can add a tiny wrapper package or test for CI.
