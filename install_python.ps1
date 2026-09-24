# Installs the regular python.org build of Python 3.13 for the current user
# (no admin rights needed). Used by _get_python.bat after the person agrees.
#
# Tries winget first. "--source winget" matters: without it winget can pick the
# Microsoft Store package instead, which is exactly the build find_python.ps1
# can't use. If winget isn't available (older or locked-down Windows), falls
# back to downloading the official installer from python.org and running it
# silently.
#
# Either route installs to %LOCALAPPDATA%\Programs\Python\Python313, which
# find_python.ps1 checks by full path - so the caller finds it straight away,
# without needing a fresh PATH (log off/on) first.
#
# Exit code 0 means Python 3.13 is now in place; anything else means it isn't.

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"  # Invoke-WebRequest is very slow with its progress bar on

$FallbackVersion = "3.13.7"
$target = Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"

$winget = Get-Command winget -ErrorAction SilentlyContinue
if ($winget) {
    Write-Host "  Installing Python 3.13 with winget (this can take a few minutes) ..."
    & $winget.Source install --id Python.Python.3.13 -e --source winget --scope user --silent `
        --accept-package-agreements --accept-source-agreements
    # winget's exit code isn't reliable here (e.g. it fails with "already
    # installed" when it is), so judge by whether the interpreter exists.
    if (Test-Path -LiteralPath $target) { exit 0 }
    Write-Host "  winget didn't complete the install - trying the python.org installer instead ..."
}

$arch = if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { "arm64" } else { "amd64" }
$url = "https://www.python.org/ftp/python/$FallbackVersion/python-$FallbackVersion-$arch.exe"
$installer = Join-Path $env:TEMP "python-$FallbackVersion-$arch.exe"

Write-Host "  Downloading Python $FallbackVersion from python.org ..."
try {
    # Windows PowerShell 5.1 can default to TLS 1.0, which python.org rejects.
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
} catch {
    Write-Host "  ERROR: Download failed: $($_.Exception.Message)"
    exit 1
}

Write-Host "  Running the Python installer (this can take a few minutes) ..."
$proc = Start-Process -FilePath $installer -Wait -PassThru -ArgumentList @(
    "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_launcher=1", "Include_test=0"
)
Remove-Item -LiteralPath $installer -ErrorAction SilentlyContinue

if (Test-Path -LiteralPath $target) { exit 0 }
Write-Host "  ERROR: The Python installer finished (exit code $($proc.ExitCode)) but Python wasn't found at $target."
exit 1
