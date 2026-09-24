# Locates a usable Python 3.10+ interpreter and prints its full path to
# stdout. Used by _get_python.bat (shared by install.bat / setup.bat) instead
# of batch-native detection, because batch's multi-line ( ) block parser
# corrupts itself when a referenced variable's *value* contains literal
# parentheses (e.g. %ProgramFiles(x86)% expands to "C:\Program Files (x86)") -
# PowerShell has no such landmine, so this does the same job without it.
#
# Handles these Windows-specific gotchas along the way:
#   - Skips the Microsoft Store "app execution alias" stubs for python.exe/py
#     (real files on PATH, but they either prompt to install from the Store or
#     launch a sandboxed Store Python that can't be relied on from Claude
#     Desktop). Store-only Python is reported as such, so the caller can offer
#     to install the regular python.org build instead.
#   - Falls back to the standard python.org install locations by full path
#     (including the newer "Python install manager" runtime folder) if nothing
#     usable is on PATH yet, since a process launched by double-clicking a .bat
#     file can still be running with a stale PATH right after installing
#     Python, until you log off/on or reboot.
#
# On success: prints the interpreter path and exits 0.
# On failure: prints a short explanation to stderr and exits 1. The caller
# offers to install Python, so this doesn't give install instructions itself.

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

function Fail([string]$message) {
    [Console]::Error.WriteLine("  " + $message)
    exit 1
}

$candidates = New-Object System.Collections.Generic.List[string]

foreach ($name in @("python", "py")) {
    # Get-Command can return several matches; add each one separately (adding
    # the array directly would join the paths into one space-separated string).
    Get-Command $name -CommandType Application -All -ErrorAction SilentlyContinue |
        ForEach-Object { if ($_.Source) { $candidates.Add($_.Source) } }
}

$roots = New-Object System.Collections.Generic.List[string]
if ($env:LOCALAPPDATA) {
    $roots.Add((Join-Path $env:LOCALAPPDATA "Programs\Python"))
    # Where the python.org "Python install manager" puts runtimes, e.g.
    # %LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe
    $roots.Add((Join-Path $env:LOCALAPPDATA "Python"))
}
if ($env:ProgramFiles) { $roots.Add($env:ProgramFiles) }
$pf86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
if ($pf86) { $roots.Add($pf86) }

foreach ($root in $roots) {
    if (Test-Path -LiteralPath $root) {
        Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like "Python3*" -or $_.Name -like "pythoncore-3*" } |
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
        # Write the bare path straight to stdout (no formatting, no extra lines)
        # so the calling batch file's for /f captures exactly this.
        [Console]::Out.WriteLine($info.Path.Trim())
        exit 0
    }
    if (-not $bestOld) { $bestOld = $info }
}

if ($bestOld) {
    Fail "Found $($bestOld.Text) at $($bestOld.Path), which is older than the required 3.10+."
}

# The aliases may have been switched off (so nothing showed up on PATH), but
# Store Python can still be installed - check for the package itself.
$storePython = $null
try {
    $storePython = Get-AppxPackage -Name "PythonSoftwareFoundation.Python.3*" -ErrorAction SilentlyContinue |
        Select-Object -First 1
} catch { }

if ($storePython -or $sawStoreAlias) {
    Fail "Only the Microsoft Store version of Python is installed. It can't be used here - the regular python.org version is needed (it can sit alongside the Store one)."
}

Fail "Python 3.10+ was not found on this computer."
