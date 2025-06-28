#!/bin/bash
set -e

echo "Running ruff linter (isort, flake, pyupgrade, etc. replacement)..."
ruff check --fix --exit-non-zero-on-fix

echo "Running ruff formatter (black replacement)..."
ruff format
