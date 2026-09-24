@echo off
REM Sets up (or rebuilds) the Python virtual environment for the Compass MCP server.
REM Run this once after copying the folder to a Windows machine (double-click or run in cmd).
setlocal EnableExtensions
cd /d "%~dp0"

REM Detection lives in find_python.ps1, not here. Batch's multi-line ( ) block
REM parser expands %VAR% inline while scanning for the block's closing paren,
REM so a variable whose *value* contains literal parentheses (e.g.
REM %ProgramFiles(x86)% -> "C:\Program Files (x86)") can corrupt that scan and
REM produce a baffling, action-at-a-distance ") was unexpected at this time"
REM error somewhere later in the script. PowerShell has no such landmine.
echo Checking for Python 3.10+ ...
set "PY="
REM Only accept a line that is an existing .exe - anything else PowerShell
REM writes to stdout (a blank line, a policy banner, etc.) is ignored rather
REM than being mistaken for the interpreter path.
for /f "usebackq delims=" %%P in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0find_python.ps1"`) do if /i "%%~xP"==".exe" if exist "%%~fP" set "PY=%%~fP"
if not defined PY (
  echo ERROR: Could not locate a usable Python 3.10+ - see message above, if any.
  pause
  exit /b 1
)
for /f "delims=" %%v in ('"%PY%" --version 2^>^&1') do set "PYVER=%%v"
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
