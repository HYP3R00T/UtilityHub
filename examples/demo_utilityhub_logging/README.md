# Demo: utilityhub_logging In Action

This demo shows what `utilityhub_logging` actually does in a realistic flow instead of just listing APIs.

It demonstrates:

- one session log file for an application run
- contextual metadata bound with `bind_context()`
- one scoped log file for a unit of work
- safe cleanup with `cleanup_logging()` and `end_scope_logging()`

## Run from this repository

From repository root:

```bash
/workspaces/UtilityHub/.venv/bin/python examples/demo_utilityhub_logging/main.py
```

The script loads the local package source from `packages/utilityhub_logging/src`, so you can validate behavior before publishing.

## What the script does

1. Creates a temporary logs directory.
2. Configures application logging for a fake worker application.
3. Binds app-level context and writes session log entries.
4. Starts a scoped log for a single job.
5. Prints the generated log file paths.
6. Prints the resulting log contents so you can inspect the output format directly.

## Expected output highlights

- an app session log path under the temporary logs directory
- a scoped log path under `scopes/job/`
- plain text log output containing `app_name`, `session_id`, `job_id`, and `subsystem`
