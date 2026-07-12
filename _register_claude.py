#!/usr/bin/env python3
"""Register (or update) the 'compass' MCP server in the Claude Desktop config.

OS-aware: picks the correct config location and venv interpreter path for the
platform it runs on. Used by both install.command (macOS) and install.bat
(Windows). Backs up any existing config first.

Usage:  python _register_claude.py <install_dir>
"""
import json
import os
import shutil
import sys


def config_path() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "Claude", "claude_desktop_config.json")
    if sys.platform == "darwin":
        return os.path.expanduser(
            "~/Library/Application Support/Claude/claude_desktop_config.json"
        )
    # Linux / other
    return os.path.expanduser("~/.config/Claude/claude_desktop_config.json")


def venv_python(dest: str) -> str:
    if sys.platform == "win32":
        return os.path.join(dest, ".venv", "Scripts", "python.exe")
    return os.path.join(dest, ".venv", "bin", "python")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python _register_claude.py <install_dir>", file=sys.stderr)
        return 2
    dest = os.path.abspath(sys.argv[1])
    cfg = config_path()

    os.makedirs(os.path.dirname(cfg), exist_ok=True)

    data = {}
    if os.path.isfile(cfg):
        shutil.copy(cfg, cfg + ".bak")
        try:
            with open(cfg, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            # Don't silently discard whatever was in there (other MCP servers,
            # settings, etc.) - a backup exists, but make sure the person
            # running this notices before we overwrite it with a blank file.
            print(
                f"   WARNING: {cfg} exists but isn't valid JSON ({e}); "
                f"a backup was saved to {cfg}.bak. Starting from an empty "
                "config - if you had other MCP servers configured, restore "
                "them from the .bak file afterward.",
                file=sys.stderr,
            )
            data = {}

    if not isinstance(data, dict):
        data = {}
    data.setdefault("mcpServers", {})
    data["mcpServers"]["compass"] = {
        "command": venv_python(dest),
        "args": [os.path.join(dest, "server.py")],
    }

    with open(cfg, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("   config updated:", cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
