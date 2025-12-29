# Demo: utilityhub_config — quick example ⚡️

A tiny, runnable script that demonstrates `utilityhub_config` and precedence order (defaults → env → runtime overrides).

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

The script prints the resolved settings and the *source* for each field (e.g., `defaults`, `env`, or `overrides`). Example output:

```
Defaults — behold the Sporkinator:
  app_name = 'sporkinator'  <-- defaults
  log_level = 'INFO'  <-- defaults
  database_url = 'sqlite:///cupcakes.db'  <-- defaults

Environment variable override (DATABASE_URL):
  database_url = 'postgres://unicorn@localhost/db-of-dreams'  <-- env (ENV:DATABASE_URL)

Runtime override:
  database_url = 'sqlite:///runtime_pancakes.db'  <-- overrides (runtime)
```

## Notes

- This example is intentionally simple: it is a script, not a package. No installation is required to run it.
- If you prefer an installable example, I can add a tiny wrapper package or test for CI.
