#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN=""
if [ -x ".venv/Scripts/python.exe" ]; then
  PYTHON_BIN=".venv/Scripts/python.exe"
elif [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=$(command -v python)
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=$(command -v python3)
elif command -v py >/dev/null 2>&1; then
  PYTHON_BIN=$(command -v py)
else
  echo "Python interpreter not found. Install Python or set PYTHON_BIN." >&2
  exit 1
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r requirements.txt

echo "$PYTHON_BIN" > .python_bin
