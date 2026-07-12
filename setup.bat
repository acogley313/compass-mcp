@echo off
REM Sets up (or rebuilds) the Python virtual environment for the Compass MCP server.
REM Run this once after copying the folder to a Windows machine (double-click or run in cmd).
setlocal EnableExtensions
cd /d "%~dp0"

echo Checking for Python 3.10+ ...
set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY (
  where py >nul 2>&1 && set "PY=py"
)
if not defined PY (
  echo.
  echo ERROR: Python is not installed or not on PATH.
  echo Download from https://www.python.org/downloads/ and check "Add Python to PATH".
  pause
  exit /b 1
)

for /f "delims=" %%v in ('%PY% --version 2^>^&1') do set "PYVER=%%v"
echo %PYVER% | findstr /C:"was not found" >nul
if not errorlevel 1 (
  echo.
  echo ERROR: Windows has a "python" shortcut on PATH, but no real Python is
  echo installed - it just opens the Microsoft Store. Fix either way:
  echo   1^) Install Python from https://www.python.org/downloads/ and tick
  echo      "Add Python to PATH", then run this again. OR
  echo   2^) Go to Settings -^> Apps -^> Advanced app settings -^> App execution
  echo      aliases, turn OFF "python.exe" / "python3.exe", then install
  echo      Python from the link above and run this again.
  pause
  exit /b 1
)
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
    echo.
    echo ERROR: Python is older than 3.10 ^(found %PYVER%^).
    echo Install a newer version from https://www.python.org/downloads/ then run this again.
    pause
    exit /b 1
)
echo OK - found %PYVER%

echo Creating virtual environment in .venv ...
%PY% -m venv .venv
if errorlevel 1 (
    echo.
    echo ERROR: Could not create venv.
    pause
    exit /b 1
)

.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
.venv\Scripts\python.exe -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies ^(check your internet connection^).
    pause
    exit /b 1
)

echo.
echo Done. Verifying connectivity to Compass ...
.venv\Scripts\python.exe server.py --selftest

echo.
echo Setup complete. Python interpreter for your Claude config:
echo   %CD%\.venv\Scripts\python.exe
echo.
echo (In claude_desktop_config.json, use DOUBLE backslashes in the path, e.g.
echo   C:\\Users\\you\\compass-mcp\\.venv\\Scripts\\python.exe )
pause
