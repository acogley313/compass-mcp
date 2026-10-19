#!/usr/bin/env python3
"""Register (or update) the 'compass' MCP server in the Claude Desktop config.

OS-aware: picks the correct config location and venv interpreter path for the
platform it runs on. Used by both install.command (macOS) and install.bat
(Windows). Backs up any existing config first.

Usage:  python _register_claude.py <install_dir> [csd_operator_init]
"""
import glob
import json
import os
import shutil
import sys


def config_path() -> str:
    if sys.platform == "win32":
        # Claude Desktop installed from the Microsoft Store runs as a packaged
        # (MSIX) app, which sandboxes app data - it never sees %APPDATA%\Claude
        # and instead reads/writes a virtualized copy under
        # LocalAppData\Packages\<PackageFamilyName>\LocalCache\Roaming\Claude.
        # The package family name has a publisher-specific hash suffix
        # ("Claude_<hash>"), so glob for it rather than hardcoding it.
        #
        # Check this FIRST, ahead of the classic path: if this script (or an
        # older version of it) already ran once on a Store-install machine, it
        # would have created a file at the classic %APPDATA%\Claude location
        # even though Claude Desktop never reads it - so "the classic file
        # exists" is not reliable evidence that it's the real one in use.
        localappdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        packaged_cfg = sorted(glob.glob(os.path.join(
            localappdata, "Packages", "Claude*", "LocalCache", "Roaming",
            "Claude", "claude_desktop_config.json",
        )))
        if packaged_cfg:
            return packaged_cfg[0]

        # No packaged config yet - if a Store-packaged install directory
        # exists at all (even before Claude has been launched once), target
        # the path it would use.
        packaged_dirs = sorted(glob.glob(os.path.join(localappdata, "Packages", "Claude*")))
        if packaged_dirs:
            return os.path.join(
                packaged_dirs[0], "LocalCache", "Roaming", "Claude", "claude_desktop_config.json"
            )

        # No Store-packaged install found at all - classic (non-Store) install.
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(appdata, "Claude", "claude_desktop_config.json")
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


def existing_config_paths() -> list[str]:
    """Every Claude Desktop config file that already exists on this machine.

    On Windows there is no reliable way to tell whether the running app reads
    the classic %APPDATA% file or the Store-packaged copy (a machine can have
    both, or switch between them across app updates), so register in all of
    them rather than guess and silently update the wrong one.
    """
    candidates = []
    if sys.platform == "win32":
        localappdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        candidates += sorted(glob.glob(os.path.join(
            localappdata, "Packages", "Claude*", "LocalCache", "Roaming",
            "Claude", "claude_desktop_config.json",
        )))
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        candidates.append(os.path.join(appdata, "Claude", "claude_desktop_config.json"))
    else:
        candidates.append(config_path())
    return [p for p in dict.fromkeys(candidates) if os.path.isfile(p)]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python _register_claude.py <install_dir> [csd_operator_init]", file=sys.stderr)
        return 2
    dest = os.path.abspath(sys.argv[1])
    csd_operator_init = sys.argv[2].strip() if len(sys.argv) > 2 else ""
    status = 0
    for cfg in existing_config_paths() or [config_path()]:
        status = register(cfg, dest, csd_operator_init) or status
    return status


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

    # Refuse to register paths that don't exist - Claude Desktop would only
    # report a cryptic "spawn ... ENOENT" when it tries to start the server.
    for path in [entry["command"]] + entry["args"]:
        if not os.path.isfile(path):
            print(f"   ERROR: {path} does not exist - not registering it.", file=sys.stderr)
            return 1

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
    if csd_operator_init:
        print(f"   CSD_OPERATOR_INIT set to: {csd_operator_init}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
