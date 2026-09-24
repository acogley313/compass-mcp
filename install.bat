@echo off
REM ============================================================================
REM  Compass MCP - one-click installer for Windows
REM
REM  Coworker workflow:
REM    1. Unzip the folder anywhere (e.g. Downloads)
REM    2. Double-click this file (install.bat)
REM
REM  It will: find Python (offering to install it if needed), copy the folder to
REM  your user folder, build the Python environment, test the Compass
REM  connection, register the server in Claude Desktop, and restart Claude
REM  Desktop so it picks the server up.
REM ============================================================================
setlocal EnableExtensions

set "SOURCE_DIR=%~dp0"
if "%SOURCE_DIR:~-1%"=="\" set "SOURCE_DIR=%SOURCE_DIR:~0,-1%"
set "DEST=%USERPROFILE%\compass-mcp"
set "VENV_PY=%DEST%\.venv\Scripts\python.exe"
set "CLAUDE_CLOSED="

echo.
echo ===============================================
echo   Compass MCP installer
echo ===============================================
echo.

REM --- 1. Find Python ---------------------------------------------------------
echo [1/5] Checking for Python 3.10+ ...
call "%SOURCE_DIR%\_get_python.bat"
if not defined PY goto fail
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
    goto fail
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
  echo   Windows may hide the file extension - check it isn't really named
  echo   credentials.ionapi.json or credentials.ionapi.txt.
  goto fail
)
echo.

REM --- 3. Build the virtual environment ---------------------------------------
REM Claude Desktop has to be closed first: a running compass server holds
REM .venv\Scripts\python.exe open (so the old venv can't be deleted), and Claude
REM Desktop can overwrite its config file while it runs (dropping step 5's edit).
echo [3/5] Building Python environment (this can take a minute) ...
powershell -NoProfile -ExecutionPolicy Bypass -File "%SOURCE_DIR%\claude_desktop.ps1" -Action Stop
set "STOP_RC=%errorlevel%"
if "%STOP_RC%"=="2" pause
if not "%STOP_RC%"=="0" set "CLAUDE_CLOSED=1"

if exist "%DEST%\.venv" rmdir /s /q "%DEST%\.venv"
if exist "%DEST%\.venv" (
  echo   ERROR: Could not remove the old environment in %DEST%\.venv.
  echo   Something is still using it - make sure Claude Desktop is fully quit,
  echo   or restart the computer, then run this again.
  goto fail
)
"%PY%" -m venv "%DEST%\.venv"
if errorlevel 1 (
  echo   ERROR: Could not create the virtual environment.
  goto fail
)
"%VENV_PY%" -m pip install --quiet --upgrade pip
"%VENV_PY%" -m pip install --quiet -r "%DEST%\requirements.txt"
if errorlevel 1 (
  echo   ERROR: Failed to install dependencies ^(check your internet connection^).
  goto fail
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
  goto fail
)
echo   OK - connected to Compass (pong)
echo.

REM --- 5. Register in Claude Desktop ------------------------------------------
echo [5/5] Registering with Claude Desktop ...
REM Close Claude Desktop again in case it was opened during the steps above.
powershell -NoProfile -ExecutionPolicy Bypass -File "%SOURCE_DIR%\claude_desktop.ps1" -Action Stop
if "%errorlevel%"=="2" pause
"%VENV_PY%" "%DEST%\_register_claude.py" "%DEST%"
if errorlevel 1 (
  echo   ERROR: Failed to update the Claude Desktop config.
  goto fail
)
echo   OK - registered the 'compass' server
echo.

echo   Starting Claude Desktop ...
powershell -NoProfile -ExecutionPolicy Bypass -File "%SOURCE_DIR%\claude_desktop.ps1" -Action Start

echo.
echo ===============================================
echo   Install complete!
echo ===============================================
echo.
echo   Claude Desktop has been restarted with the Compass server added.
echo   In a chat, type:  Ping Compass   to check the connection.
echo.
echo   If Compass doesn't show up, fully quit Claude Desktop ^(right-click its
echo   icon in the system tray - Quit^) and open it again.
echo.
pause
exit /b 0

:fail
REM Don't leave Claude Desktop closed just because the install failed.
if defined CLAUDE_CLOSED powershell -NoProfile -ExecutionPolicy Bypass -File "%SOURCE_DIR%\claude_desktop.ps1" -Action Start
echo.
pause
exit /b 1
