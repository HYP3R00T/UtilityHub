# Extension Schemas

Use extension schemas when your application needs open-ended named config sections whose shape is not known until runtime.

This is useful for plugin-style configuration such as:

```toml
[plugins.component_a]
threshold = 0.8
model_path = "~/models/a.pth"

[plugins.component_b]
enabled = true
```

## Runtime registration

Register named schemas with `load_settings()` using `extension_schemas`.

```python
from pydantic import BaseModel
from utilityhub_config import load_settings

class ComponentConfig(BaseModel):
    threshold: float = 0.5
    model_path: str = "~/default/path"

class AppConfig(BaseModel):
    app_name: str = "myapp"
    plugins: dict[str, object] = {}

settings, metadata = load_settings(
    AppConfig,
    extension_root="plugins",
    extension_schemas={"component_a": ComponentConfig},
)

component_a = metadata.extension_configs["component_a"]
print(component_a.threshold)
print(component_a.model_path)
```

In this example, `plugins.component_a` is validated against `ComponentConfig` and the resulting model instance is available in `metadata.extension_configs`.

## Defaults and missing sections

If a registered section is absent from all config sources, its schema defaults are still used.

```python
settings, metadata = load_settings(
    AppConfig,
    extension_root="plugins",
    extension_schemas={"component_a": ComponentConfig},
)

assert metadata.extension_configs["component_a"].threshold == 0.5
```

## Unknown extension sections

Use `unknown_extension_policy` to control behavior when an unregistered section appears under `extension_root`.

- `ignore` (default): silently ignore unknown section names
- `warn`: emit a `UserWarning`
- `error`: raise `ConfigError`

```python
settings, metadata = load_settings(
    AppConfig,
    extension_root="plugins",
    extension_schemas={"component_a": ComponentConfig},
    unknown_extension_policy="warn",
)
```

## Disabling env vars for extension-loaded configs

If you need deterministic config loading without environment variables, set `env_vars=False`.

```python
settings, metadata = load_settings(
    AppConfig,
    env_vars=False,
    extension_root="plugins",
    extension_schemas={"component_a": ComponentConfig},
)
```
