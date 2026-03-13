# Demo: Nested Source Tracking (With Personality)

This demo is focused on the nested metadata source-tracking fix and keeps a playful tone so the output is easier to scan.

It shows that all of the following now resolve correctly:
- model.backend
- model.device
- inference.despill_strength

It also proves nested env overrides with double-underscore names, for example EZCK_MODEL__DEVICE.

## Run from this repository

From repository root:

```bash
/workspaces/UtilityHub/.venv/bin/python examples/demo_utilityhub_config/main.py
```

The script loads the local package source from packages/utilityhub_config/src, so you can validate behavior before publishing to PyPI.

## What the script does

1. Creates a temporary project config file named ezck.yaml with nested values.
2. Applies a nested environment override via EZCK_MODEL__DEVICE.
3. Applies a nested runtime override for model.backend.
4. Prints value plus metadata source for top-level and nested paths.

The output is intentionally narrative, but the checks are explicit so you can verify release behavior quickly.

## Expected output highlights

- metadata.get_source("model.backend") reports overrides.
- metadata.get_source("model.device") reports env with ENV:EZCK_MODEL__DEVICE.
- metadata.get_source("inference.despill_strength") reports project.
