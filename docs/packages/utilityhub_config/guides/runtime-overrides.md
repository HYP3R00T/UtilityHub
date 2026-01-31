# Runtime Overrides

Override values at runtime (highest precedence).

## Basic Usage

```python
settings, _ = load_settings(
    Config,
    overrides={
        "debug": True,
        "workers": 16
    }
)
```

## Use Cases

### Testing

```python
def test_with_debug():
    settings, _ = load_settings(Config, overrides={"debug": True})
    assert settings.debug is True
```

### CLI Arguments

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--workers", type=int)
args = parser.parse_args()

overrides = {}
if args.workers:
    overrides["workers"] = args.workers

settings, _ = load_settings(Config, overrides=overrides)
```

### Feature Flags

```python
overrides = {}
if experimental_mode:
    overrides["use_new_engine"] = True

settings, _ = load_settings(Config, overrides=overrides)
```

[← Back to Guides](./index.md)
