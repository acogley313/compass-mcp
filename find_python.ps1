# Locates a usable Python 3.10+ interpreter and prints its full path to
# stdout. Used by install.bat / setup.bat instead of batch-native detection,
# because batch's multi-line ( ) block parser corrupts itself when a
# referenced variable's *value* contains literal parentheses (e.g.
# %ProgramFiles(x86)% expands to "C:\Program Files (x86)") - PowerShell has
# no such landmine, so this does the same job without it.
#
# Handles two Windows-specific gotchas along the way:
#   - Skips the Microsoft Store "app execution alias" stub for python.exe/py
#     (it's a real file on PATH, but running it just prompts to install from
#     the Store instead of running Python).
#   - Falls back to the standard python.org install locations by full path
#     if nothing usable is on PATH yet, since a process launched by
#     double-clicking a .bat file can still be running with a stale PATH
#     right after installing Python, until you log off/on or reboot.
#
# On success: prints the interpreter path and exits 0.
# On failure: prints a diagnostic explaining what (if anything) was found,
# to stderr, and exits 1.

$ErrorActionPreference = "Stop"

function Get-VersionInfo([string]$path) {
    if ($path -match '\\WindowsApps\\') { return $null }
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    try {
        $out = & $path --version 2>&1
    } catch {
        return $null
    }
    if ($LASTEXITCODE -ne 0) { return $null }
    $text = ($out | Out-String).Trim()
    if ($text -notmatch 'Python\s+(\d+)\.(\d+)') { return $null }
    return [PSCustomObject]@{
        Path  = $path
        Major = [int]$Matches[1]
        Minor = [int]$Matches[2]
        Text  = $text
    }
}

$candidates = New-Object System.Collections.Generic.List[string]

foreach ($name in @("python", "py")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { $candidates.Add($cmd.Source) }
}

$roots = New-Object System.Collections.Generic.List[string]
if ($env:LOCALAPPDATA) { $roots.Add((Join-Path $env:LOCALAPPDATA "Programs\Python")) }
if ($env:ProgramFiles) { $roots.Add($env:ProgramFiles) }
$pf86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
if ($pf86) { $roots.Add($pf86) }

foreach ($root in $roots) {
    if (Test-Path -LiteralPath $root) {
        Get-ChildItem -LiteralPath $root -Directory -Filter "Python3*" -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { $candidates.Add((Join-Path $_.FullName "python.exe")) }
    }
}

if ($env:LOCALAPPDATA) {
    $launcher = Join-Path $env:LOCALAPPDATA "Programs\Python\Launcher\py.exe"
    if (Test-Path -LiteralPath $launcher) { $candidates.Add($launcher) }
}

$sawStoreAlias = $false
$bestOld = $null

foreach ($path in $candidates) {
    if ($path -match '\\WindowsApps\\') { $sawStoreAlias = $true; continue }
    $info = Get-VersionInfo $path
    if (-not $info) { continue }
    if (($info.Major -gt 3) -or ($info.Major -eq 3 -and $info.Minor -ge 10)) {
        Write-Output $info.Path
        exit 0
    }
    if (-not $bestOld) { $bestOld = $info }
}

if ($bestOld) {
    Write-Error "Found $($bestOld.Text) at $($bestOld.Path), which is older than the required 3.10+. Install a newer version from https://www.python.org/downloads/ then run this again."
    exit 1
}

if ($sawStoreAlias) {
    Write-Error @"
Windows has a "python"/"py" shortcut on PATH, but no real Python is
installed - it just opens the Microsoft Store. Fix either way:
  1) Install Python from https://www.python.org/downloads/ and tick
     "Add Python to PATH", then run this again. OR
  2) Go to Settings -> Apps -> Advanced app settings -> App execution
     aliases, turn OFF "python.exe" / "python3.exe", then install
     Python from the link above and run this again.
"@
    exit 1
}

Write-Error @"
Python is not installed or not on PATH.
Install it from https://www.python.org/downloads/ and tick "Add Python
to PATH" during setup, then run this again.

If you just installed Python and this still fails, log off and back on
(or restart the computer), then run this again - Windows needs a fresh
session to pick up some installs.
"@
exit 1
