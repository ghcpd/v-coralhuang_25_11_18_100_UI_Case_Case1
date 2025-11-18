#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .python_bin ]; then
  echo "Please run ./setup.sh first to generate .python_bin." >&2
  exit 1
fi

PYTHON_BIN=$(cat .python_bin)
"$PYTHON_BIN" -m pytest tests/test_fixed_plugin.py
