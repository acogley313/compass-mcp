#!/usr/bin/env bash
# =============================================================================
# Compass MCP — one-click installer for macOS
#
# Coworker workflow:
#   1. Unzip the folder anywhere (e.g. Downloads)
#   2. Double-click this file (install.command)
#
# It will: move the folder to your home folder, build the Python environment,
# test the Compass connection, and register the server in Claude Desktop.
# =============================================================================

set -uo pipefail

# Resolve the folder this script lives in (works no matter where it's run from).
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/compass-mcp"

bold() { printf "\033[1m%s\033[0m\n" "$1"; }
ok()   { printf "\033[32m✓ %s\033[0m\n" "$1"; }
err()  { printf "\033[31m✗ %s\033[0m\n" "$1"; }

echo
bold "==============================================="
bold "  Compass MCP installer"
bold "==============================================="
echo

# --- 1. Check Python -----------------------------------------------------------
bold "[1/5] Checking for Python 3.10+ ..."
if ! command -v python3 >/dev/null 2>&1; then
  err "Python 3 is not installed."
  echo "    Install it from https://www.python.org/downloads/ then run this again."
  echo
  read -r -p "Press Return to close."
  exit 1
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
  err "Python is older than 3.10 ($(python3 --version))."
  echo "    Install a newer version from https://www.python.org/downloads/ then run this again."
  echo
  read -r -p "Press Return to close."
  exit 1
fi
ok "Found $(python3 --version)"
echo

# --- 2. Move folder into place -------------------------------------------------
bold "[2/5] Installing to $DEST ..."
if [ "$SOURCE_DIR" != "$DEST" ]; then
  mkdir -p "$DEST"
  # Copy everything except the throwaway build artifacts.
  rsync -a --exclude '.venv' --exclude '__pycache__' --exclude '*.bak' \
        "$SOURCE_DIR"/ "$DEST"/ 2>/dev/null \
    || cp -R "$SOURCE_DIR"/. "$DEST"/
  ok "Files copied to $DEST"
else
  ok "Already running from $DEST"
fi
cd "$DEST" || { err "Could not enter $DEST"; read -r -p "Press Return to close."; exit 1; }

if [ ! -f "$DEST/credentials.ionapi" ]; then
  err "credentials.ionapi is missing."
  echo "    Get a service-account .ionapi file from your Infor ION API portal"
  echo "    (Infor OS Portal -> API Gateway -> Authorized Apps), rename it to"
  echo "    \"credentials.ionapi\", and place it in $SOURCE_DIR"
  echo "    (next to install.command) before running this installer."
  read -r -p "Press Return to close."
  exit 1
fi
echo

# --- 3. Build the virtual environment -----------------------------------------
bold "[3/5] Building Python environment (this can take a minute) ..."
rm -rf "$DEST/.venv"
python3 -m venv "$DEST/.venv"
"$DEST/.venv/bin/python" -m pip install --quiet --upgrade pip
if ! "$DEST/.venv/bin/python" -m pip install --quiet -r "$DEST/requirements.txt"; then
  err "Failed to install dependencies (check your internet connection)."
  read -r -p "Press Return to close."
  exit 1
fi
ok "Dependencies installed"
echo

# --- 4. Test the Compass connection -------------------------------------------
bold "[4/5] Testing the Compass connection ..."
if "$DEST/.venv/bin/python" "$DEST/server.py" --selftest 2>&1 | grep -q '"response": "pong"'; then
  ok "Connected to Compass successfully (pong)"
else
  err "Could not reach Compass / authentication failed."
  echo "    Run this for details:"
  echo "      $DEST/.venv/bin/python $DEST/server.py --selftest"
  echo "    The credentials may have expired — get a fresh .ionapi from the Infor portal."
  read -r -p "Press Return to close."
  exit 1
fi
echo

# --- 5. Register in Claude Desktop --------------------------------------------
bold "[5/5] Registering with Claude Desktop ..."
if ! "$DEST/.venv/bin/python" "$DEST/_register_claude.py" "$DEST"; then
  err "Failed to update the Claude Desktop config."
  read -r -p "Press Return to close."
  exit 1
fi
ok "Registered the 'compass' server in Claude Desktop"
echo

bold "==============================================="
ok   "Install complete!"
bold "==============================================="
echo
echo "  LAST STEP — restart Claude Desktop:"
echo "    1. Quit Claude Desktop completely with  Cmd + Q  (not just the window)"
echo "    2. Reopen it"
echo "    3. In a chat, type:  Ping Compass to check the connection"
echo
read -r -p "Press Return to close this window."
