# Closes or starts Claude Desktop for install.bat.
#
#   -Action Stop   Force-closes Claude Desktop if it's running, and waits for
#                  it to exit. Exit code 0 if it wasn't running, 1 if it was
#                  (and is now closed), 2 if it wouldn't close.
#   -Action Start  Launches Claude Desktop.
#
# Why force-close: Claude Desktop rewrites claude_desktop_config.json with its
# own settings while it runs, which can silently drop the 'compass' entry the
# installer just added. It also holds .venv\Scripts\python.exe open while the
# compass server is running, so the venv can't be rebuilt underneath it.
#
# Only processes running from Claude Desktop's install folders are matched,
# never just any "claude.exe" - the Claude Code CLI uses that name too, and
# killing someone's terminal session would be a nasty surprise.
#   Classic install:  %LOCALAPPDATA%\AnthropicClaude\app-<version>\claude.exe
#   Microsoft Store:  C:\Program Files\WindowsApps\Claude_<version>_...\app\claude.exe

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Stop", "Start")]
    [string]$Action
)

function Get-ClaudeDesktopProcesses {
    Get-Process -Name "claude" -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -and ($_.Path -match '\\AnthropicClaude\\' -or $_.Path -match '\\WindowsApps\\Claude_')
    }
}

if ($Action -eq "Stop") {
    $procs = @(Get-ClaudeDesktopProcesses)
    if ($procs.Count -eq 0) { exit 0 }
    Write-Host "  Closing Claude Desktop (it will be reopened when the install finishes) ..."
    $procs | Stop-Process -Force -ErrorAction SilentlyContinue
    for ($i = 0; $i -lt 30; $i++) {
        if (@(Get-ClaudeDesktopProcesses).Count -eq 0) { exit 1 }
        Start-Sleep -Milliseconds 500
    }
    Write-Host "  WARNING: Claude Desktop is still running. Quit it from the system tray"
    Write-Host "  (right-click its icon - Quit), then press a key to continue."
    exit 2
}

# Start: prefer the Start-menu entry, which works for both the classic and the
# Microsoft Store install (a Store app can't be launched by its .exe path).
$app = $null
try {
    $app = Get-StartApps -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq "Claude" } | Select-Object -First 1
} catch { }
if ($app) {
    Start-Process -FilePath "explorer.exe" -ArgumentList "shell:AppsFolder\$($app.AppID)"
    exit 0
}

$stub = Join-Path $env:LOCALAPPDATA "AnthropicClaude\claude.exe"
if (Test-Path -LiteralPath $stub) {
    Start-Process -FilePath $stub
    exit 0
}

Write-Host "  Couldn't find Claude Desktop to start it - open it from the Start menu."
exit 0
