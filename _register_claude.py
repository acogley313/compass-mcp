#!/usr/bin/env python3
"""Register (or update) the 'compass' MCP server in the Claude Desktop config.

OS-aware: picks the correct config location and venv interpreter path for the
platform it runs on. Used by both install.command (macOS) and install.bat
(Windows). Backs up any existing config first.

Usage:  python _register_claude.py <install_dir>
"""
import glob
import json
import os
import shutil
import sys


def config_path() -> str:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        classic = os.path.join(appdata, "Claude", "claude_desktop_config.json")
        if os.path.isfile(classic):
            return classic

        # Claude Desktop installed from the Microsoft Store runs as a packaged
        # (MSIX) app, which sandboxes app data - it never sees %APPDATA%\Claude
        # and instead reads/writes a virtualized copy under
        # LocalAppData\Packages\<PackageFamilyName>\LocalCache\Roaming\Claude.
        # The package family name has a publisher-specific hash suffix
        # ("Claude_<hash>"), so glob for it rather than hardcoding it.
        localappdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        packaged_cfg = sorted(glob.glob(os.path.join(
            localappdata, "Packages", "Claude*", "LocalCache", "Roaming",
            "Claude", "claude_desktop_config.json",
        )))
        if packaged_cfg:
            return packaged_cfg[0]

        # Neither config exists yet (e.g. Claude Desktop has never been
        # launched). If a Store-packaged install directory exists, target the
        # path it would use; otherwise assume the classic (non-Store) install.
        packaged_dirs = sorted(glob.glob(os.path.join(localappdata, "Packages", "Claude*")))
        if packaged_dirs:
            return os.path.join(
                packaged_dirs[0], "LocalCache", "Roaming", "Claude", "claude_desktop_config.json"
            )

        return classic
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
