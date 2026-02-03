#!/usr/bin/env bash
set -euo pipefail

uv run python -m ruff format .
uv run python -m ruff check .
uv run python -m mypy .
uv run python -m pytest
uv run python tests/e2e_linker_validation.py
uv run python tests/e2e_generate_test_output.py
