#!/usr/bin/env bash
# Sets up (or rebuilds) the Python virtual environment for the Compass MCP server.
# Run this once after copying the folder to a new machine.
set -euo pipefail
cd "$(dirname "$0")"

echo "Creating virtual environment in .venv ..."
python3 -m venv .venv
./.venv/bin/pip install --quiet --upgrade pip
./.venv/bin/pip install --quiet -r requirements.txt

echo
echo "Done. Verifying connectivity to Compass ..."
./.venv/bin/python server.py --selftest

echo
echo "Setup complete. Python interpreter for your Claude config:"
echo "  $(pwd)/.venv/bin/python"
