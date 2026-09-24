@echo off
REM Sets up (or rebuilds) the Python virtual environment for the Compass MCP server
REM IN THIS FOLDER, without copying anything or touching Claude Desktop's config.
REM For a normal install, use install.bat instead - this is for manual setups
REM (see "Manual setup" in README.md) and for rebuilding a venv in place.
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo   This is the MANUAL setup script. It only builds the Python environment
echo   in this folder - it does NOT install Compass into Claude Desktop.
echo   For a normal install, use install.bat instead.
echo.
choice /c YN /m "  Run install.bat instead (recommended)"
if errorlevel 2 goto manual
call "%~dp0install.bat"
exit /b

:manual
echo.
echo Checking for Python 3.10+ ...
call "%~dp0_get_python.bat"
if not defined PY (
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
echo Python environment ready. Claude Desktop has NOT been configured - add this
echo interpreter to claude_desktop_config.json yourself ^(see README.md^):
echo   %CD%\.venv\Scripts\python.exe
echo.
echo (In claude_desktop_config.json, use DOUBLE backslashes in the path, e.g.
echo   C:\\Users\\you\\compass-mcp\\.venv\\Scripts\\python.exe )
pause
