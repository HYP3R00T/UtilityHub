#!/bin/bash

if ! command -v cz >/dev/null; then
  uv run pip install --user pipx
  uv run pipx install commitizen
fi

if [ ! -f .git/hooks/pre-commit ]; then
  uv run pre-commit install
fi

if [ ! -f .git/hooks/commit-msg ]; then
  uv run pre-commit install --hook-type commit-msg
fi
