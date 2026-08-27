@echo off
REM ============================================================================
REM  Compass MCP - one-click installer for Windows
REM
REM  Coworker workflow:
REM    1. Unzip the folder anywhere (e.g. Downloads)
REM    2. Double-click this file (install.bat)
REM
REM  It will: copy the folder to your user folder, build the Python environment,
REM  test the Compass connection, and register the server in Claude Desktop.
REM ============================================================================
setlocal EnableExtensions

set "SOURCE_DIR=%~dp0"
if "%SOURCE_DIR:~-1%"=="\" set "SOURCE_DIR=%SOURCE_DIR:~0,-1%"
set "DEST=%USERPROFILE%\compass-mcp"
set "VENV_PY=%DEST%\.venv\Scripts\python.exe"

echo.
echo ===============================================
echo   Compass MCP installer
echo ===============================================
echo.

REM --- 1. Find Python ---------------------------------------------------------
REM Detection lives in find_python.ps1, not here. Batch's multi-line ( ) block
REM parser expands %VAR% inline while scanning for the block's closing paren,
REM so a variable whose *value* contains literal parentheses (e.g.
REM %ProgramFiles(x86)% -> "C:\Program Files (x86)") can corrupt that scan and
REM produce a baffling, action-at-a-distance ") was unexpected at this time"
REM error somewhere later in the script. PowerShell has no such landmine.
echo [1/5] Checking for Python 3.10+ ...
set "PY="
for /f "usebackq delims=" %%P in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%SOURCE_DIR%\find_python.ps1"`) do set "PY=%%P"
if not defined PY (
  pause
  exit /b 1
)
for /f "delims=" %%v in ('"%PY%" --version 2^>^&1') do set "PYVER=%%v"
echo   OK - found %PYVER%
echo.

REM --- 2. Copy folder into place ----------------------------------------------
echo [2/5] Installing to %DEST% ...
if /I not "%SOURCE_DIR%"=="%DEST%" (
  if not exist "%DEST%" mkdir "%DEST%"
  robocopy "%SOURCE_DIR%" "%DEST%" /E /XD ".venv" "__pycache__" /XF "*.bak" /NFL /NDL /NJH /NJS /NP >nul
  if errorlevel 8 (
    echo   ERROR: Failed to copy files to %DEST%.
    pause
    exit /b 1
  )
  echo   OK - files copied
) else (
  echo   OK - already running from %DEST%
)

if not exist "%DEST%\credentials.ionapi" (
  echo   ERROR: credentials.ionapi is missing.
  echo   Get a service-account .ionapi file from your Infor ION API portal
  echo   ^(Infor OS Portal -^> API Gateway -^> Authorized Apps^), rename it to
  echo   "credentials.ionapi", and place it in %SOURCE_DIR%
  echo   ^(next to install.bat^) before running this installer.
  pause
  exit /b 1
)
echo.

REM --- 3. Build the virtual environment ---------------------------------------
echo [3/5] Building Python environment (this can take a minute) ...
if exist "%DEST%\.venv" rmdir /s /q "%DEST%\.venv"
"%PY%" -m venv "%DEST%\.venv"
if errorlevel 1 (
  echo   ERROR: Could not create the virtual environment.
  pause
  exit /b 1
)
"%VENV_PY%" -m pip install --quiet --upgrade pip
"%VENV_PY%" -m pip install --quiet -r "%DEST%\requirements.txt"
if errorlevel 1 (
  echo   ERROR: Failed to install dependencies (check your internet connection).
  pause
  exit /b 1
)
echo   OK - dependencies installed
echo.

REM --- 4. Test the Compass connection -----------------------------------------
echo [4/5] Testing the Compass connection ...
"%VENV_PY%" "%DEST%\server.py" --selftest 2>&1 | findstr /C:"\"response\": \"pong\"" >nul
if errorlevel 1 (
  echo   ERROR: Could not reach Compass / authentication failed.
  echo   Run this for details:
  echo     "%VENV_PY%" "%DEST%\server.py" --selftest
  echo   The credentials may have expired - get a fresh .ionapi from the Infor portal.
  pause
  exit /b 1
)
echo   OK - connected to Compass (pong)
echo.

REM --- 5. Register in Claude Desktop ------------------------------------------
echo [5/5] Registering with Claude Desktop ...
"%VENV_PY%" "%DEST%\_register_claude.py" "%DEST%"
if errorlevel 1 (
  echo   ERROR: Failed to update the Claude Desktop config.
  pause
  exit /b 1
)
echo   OK - registered the 'compass' server
echo.

echo ===============================================
echo   Install complete!
echo ===============================================
echo.
echo   LAST STEP - restart Claude Desktop:
echo     1. Quit Claude Desktop completely (right-click the taskbar icon - Quit,
echo        or close it from the system tray - do not just close the window)
echo     2. Reopen it
echo     3. In a chat, type:  Ping Compass to check the connection
echo.
pause
