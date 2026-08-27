@echo off
REM Sets up (or rebuilds) the Python virtual environment for the Compass MCP server.
REM Run this once after copying the folder to a Windows machine (double-click or run in cmd).
setlocal EnableExtensions
cd /d "%~dp0"

REM %ProgramFiles(x86)% has parens in its own name, which breaks cmd's paren
REM matching if referenced inside a multi-line ( ) block below - pull it into
REM a plain variable once, up front, where that's not an issue.
set "PFX86=%ProgramFiles(x86)%"

echo Checking for Python 3.10+ ...
set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY (
  where py >nul 2>&1 && set "PY=py"
)

REM If Python was *just* installed, this window can still be running with a
REM stale PATH - double-clicking a .bat file inherits Explorer's cached
REM environment, which doesn't pick up a new install until you log off/on
REM or reboot. Fall back to the standard python.org install locations by
REM full path so a fresh install works right away without that.
if not defined PY (
  for %%B in (
    "%LocalAppData%\Programs\Python"
    "%ProgramFiles%"
    "%PFX86%"
  ) do (
    if not defined PY (
      for /f "delims=" %%D in ('dir /b /ad /o-n "%%~B\Python3*" 2^>nul') do (
        if not defined PY if exist "%%~B\%%D\python.exe" set "PY=%%~B\%%D\python.exe"
      )
    )
  )
)
if not defined PY (
  if exist "%LocalAppData%\Programs\Python\Launcher\py.exe" set "PY=%LocalAppData%\Programs\Python\Launcher\py.exe"
)

if not defined PY (
  echo.
  echo ERROR: Python is not installed or not on PATH.
  echo Download from https://www.python.org/downloads/ and check "Add Python to PATH".
  echo.
  echo If you just installed Python and this still fails, log off and back
  echo on ^(or restart the computer^), then run this again - Windows needs a
  echo fresh session to pick up some installs.
  pause
  exit /b 1
)

for /f "delims=" %%v in ('"%PY%" --version 2^>^&1') do set "PYVER=%%v"
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
"%PY%" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
    echo.
    echo ERROR: Python is older than 3.10 ^(found %PYVER%^).
    echo Install a newer version from https://www.python.org/downloads/ then run this again.
    pause
    exit /b 1
)
echo OK - found %PYVER%

echo Creating virtual environment in .venv ...
"%PY%" -m venv .venv
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
