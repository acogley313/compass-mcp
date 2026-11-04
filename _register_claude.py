#!/usr/bin/env python3
"""Register (or update) the 'compass' MCP server in the Claude Desktop config.

OS-aware: picks the config location(s) and venv interpreter path for the
platform it runs on - on Windows that's every location a Store/MSIX or classic
Claude Desktop install might read (see windows_config_paths). Used by both
install.command (macOS) and install.bat (Windows). Backs up any existing config
first.

Usage:  python _register_claude.py <install_dir> [csd_operator_init]
"""
import glob
import json
import os
import shutil
import sys


CONFIG_NAME = "claude_desktop_config.json"


def windows_config_paths() -> list[str]:
    r"""Every place a Windows Claude Desktop install might read its config from.

    There is no reliable way to tell from outside the app which one the running
    copy uses - it has moved twice and differs by install type and version - so
    the installer writes the 'compass' entry into all of them. Each file only
    gains/updates its own 'compass' entry, so an unused copy is harmless.

      1. %LOCALAPPDATA%\Claude-Data\claude_<id>\claude_desktop_config.json
         Current Microsoft Store / MSIX builds (the WinGet and claude-setup.exe
         installs are MSIX too). The app migrated its user data here and now
         ignores the old packaged location below.
      2. %LOCALAPPDATA%\Packages\Claude_<hash>\LocalCache\Roaming\Claude\...
         Older MSIX builds: a packaged app's writes to %APPDATA% are virtualized
         into this per-package folder.
      3. %APPDATA%\Claude\claude_desktop_config.json
         Classic (non-Store) installs. Always written: MSIX apps can also fall
         back to reading the real %APPDATA% when they have no private copy.
    """
    localappdata = os.environ.get("LOCALAPPDATA") or os.path.join(
        os.path.expanduser("~"), "AppData", "Local")
    appdata = os.environ.get("APPDATA") or os.path.join(
        os.path.expanduser("~"), "AppData", "Roaming")

    paths = []
    for d in sorted(glob.glob(os.path.join(localappdata, "Claude-Data", "claude_*"))):
        if os.path.isdir(d):
            paths.append(os.path.join(d, CONFIG_NAME))
    for d in sorted(glob.glob(os.path.join(localappdata, "Packages", "Claude_*"))):
        if os.path.isdir(d):
            paths.append(os.path.join(d, "LocalCache", "Roaming", "Claude", CONFIG_NAME))
    paths.append(os.path.join(appdata, "Claude", CONFIG_NAME))
    # Windows paths are case-insensitive; drop duplicates that differ only by case.
    seen, unique = set(), []
    for p in paths:
        key = os.path.normcase(os.path.normpath(p))
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def config_paths() -> list[str]:
    if sys.platform == "win32":
        return windows_config_paths()
    if sys.platform == "darwin":
        return [os.path.expanduser(
            "~/Library/Application Support/Claude/" + CONFIG_NAME
        )]
    # Linux / other
    return [os.path.expanduser("~/.config/Claude/" + CONFIG_NAME)]


def venv_python(dest: str) -> str:
    if sys.platform == "win32":
        return os.path.join(dest, ".venv", "Scripts", "python.exe")
    return os.path.join(dest, ".venv", "bin", "python")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python _register_claude.py <install_dir> [csd_operator_init]", file=sys.stderr)
        return 2
    dest = os.path.abspath(sys.argv[1])
    csd_operator_init = sys.argv[2].strip() if len(sys.argv) > 2 else ""

    # Refuse to register paths that don't exist - Claude Desktop would only
    # report a cryptic "spawn ... ENOENT" when it tries to start the server.
    for path in (venv_python(dest), os.path.join(dest, "server.py")):
        if not os.path.isfile(path):
            print(f"   ERROR: {path} does not exist - not registering it.", file=sys.stderr)
            return 1

    targets = config_paths()
    ok = 0
    for cfg in targets:
        try:
            if register(cfg, dest, csd_operator_init) == 0:
                ok += 1
        except Exception as e:  # one unwritable location shouldn't stop the rest
            print(f"   WARNING: could not update {cfg}: {e}", file=sys.stderr)

    if ok == 0:
        print("   ERROR: could not write any Claude Desktop config file.", file=sys.stderr)
        return 1
    if csd_operator_init:
        print(f"   CSD_OPERATOR_INIT set to: {csd_operator_init}")
    if ok < len(targets):
        print(f"   ({ok} of {len(targets)} config locations updated - see warnings above)")
    return 0


def register(cfg: str, dest: str, csd_operator_init: str) -> int:
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
    existing = data["mcpServers"].get("compass")
    existing_env = existing.get("env") if isinstance(existing, dict) else None
    entry = {
        "command": venv_python(dest),
        "args": [os.path.join(dest, "server.py")],
    }
    env = dict(existing_env) if isinstance(existing_env, dict) else {}
    if csd_operator_init:
        env["CSD_OPERATOR_INIT"] = csd_operator_init
    if env:
        entry["env"] = env

    data["mcpServers"]["compass"] = entry

    with open(cfg, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Read it back to confirm the entry actually landed in the file.
    try:
        with open(cfg, encoding="utf-8") as f:
            written = json.load(f)
    except Exception as e:
        print(f"   ERROR: could not read back {cfg}: {e}", file=sys.stderr)
        return 1
    if written.get("mcpServers", {}).get("compass") != entry:
        print(f"   ERROR: the 'compass' entry is missing from {cfg} after writing it.", file=sys.stderr)
        return 1

    print("   config updated:", cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
