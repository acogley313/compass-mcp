@echo off
REM Shared by install.bat and setup.bat (via "call"): sets PY to the full path of
REM a usable Python 3.10+, offering to install one if none is found. PY is left
REM undefined if there's still no usable Python at the end.
REM
REM No setlocal here on purpose - PY has to survive back into the caller.
REM Uses goto rather than ( ) blocks: see find_python.ps1 for why multi-line
REM blocks are a landmine in batch.

set "PY="
call :find
if defined PY goto :eof

echo.
echo   Python 3.10 or newer is needed. This installer can set up Python 3.13
echo   for you from python.org - just for your Windows account, no admin needed.
echo.
choice /c YN /m "  Install Python 3.13 now"
if errorlevel 2 goto declined

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_python.ps1"
call :find
if defined PY goto :eof

echo.
echo   ERROR: Python still couldn't be found after installing it. Close this
echo   window, open a new one, and run the installer again. If that fails too,
echo   install Python 3.13 from https://www.python.org/downloads/windows/
echo   ^(tick "Add python.exe to PATH"^) and run the installer again.
goto :eof

:declined
echo.
echo   Install Python 3.10+ from https://www.python.org/downloads/windows/
echo   ^(tick "Add python.exe to PATH"^), then run the installer again.
goto :eof

:find
REM Only accept a line that is an existing .exe - anything else PowerShell
REM writes to stdout (a blank line, a policy banner, etc.) is ignored rather
REM than being mistaken for the interpreter path.
for /f "usebackq delims=" %%P in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0find_python.ps1"`) do if /i "%%~xP"==".exe" if exist "%%~fP" set "PY=%%~fP"
goto :eof
