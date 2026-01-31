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

1. `~/.config/config/config.yaml` or `config.toml`
2. `./config.yaml` or `./config.toml`
3. `./.env`

## With App Name

```python
settings, _ = load_settings(Config, app_name="myapp")
```

Checks:
1. `~/.config/myapp/config.yaml` or `config.toml`
2. `./myapp.yaml` or `./myapp.toml`
3. `./.env`

[← Back to Guides](./index.md)
