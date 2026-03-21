# Configuration Files

## TOML Format

`config.toml`:
```toml
database_url = "postgres://localhost/prod"
debug = false
workers = 8
```

## YAML Format

Install: `pip install pyyaml`

`config.yaml`:
```yaml
database_url: postgres://localhost/prod
debug: false
workers: 8
```

## .env Format

Install: `pip install python-dotenv`

`.env`:
```bash
DATABASE_URL=postgres://localhost/prod
DEBUG=false
WORKERS=8
```

## Auto-Discovery

`load_settings()` checks in order:

1. `~/.config/config/config.toml` and `~/.config/config/config.yaml`
2. `./config.toml` and `./config.yaml`
3. Files in `./config/` matching `*.toml`, `*.yaml`, `*.yml`
4. `./.env`

## With App Name

```python
settings, _ = load_settings(Config, app_name="myapp")
```

Checks:
1. `~/.config/myapp/myapp.toml` and `~/.config/myapp/myapp.yaml`
2. `./myapp.toml` and `./myapp.yaml`
3. Files in `./config/` matching `*.toml`, `*.yaml`, `*.yml`
4. `./.env`

[← Back to Guides](./index.md)
