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
echo [1/5] Checking for Python 3.10+ ...
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
REM
REM NOTE: these stay single-line (no ( ) block) on purpose. %ProgramFiles(x86)%
REM expands to a value that itself contains literal parentheses ("C:\Program
REM Files (x86)"), which corrupts cmd's paren-matching if it ever ends up
REM inside a multi-line ( ) block - single-line "if ... do ..." has no block
REM to match, so it's immune to that.
if not defined PY for /f "delims=" %%D in ('dir /b /ad /o-n "%LocalAppData%\Programs\Python\Python3*" 2^>nul') do if not defined PY if exist "%LocalAppData%\Programs\Python\%%D\python.exe" set "PY=%LocalAppData%\Programs\Python\%%D\python.exe"
if not defined PY for /f "delims=" %%D in ('dir /b /ad /o-n "%ProgramFiles%\Python3*" 2^>nul') do if not defined PY if exist "%ProgramFiles%\%%D\python.exe" set "PY=%ProgramFiles%\%%D\python.exe"
if not defined PY for /f "delims=" %%D in ('dir /b /ad /o-n "%ProgramFiles(x86)%\Python3*" 2^>nul') do if not defined PY if exist "%ProgramFiles(x86)%\%%D\python.exe" set "PY=%ProgramFiles(x86)%\%%D\python.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Launcher\py.exe" set "PY=%LocalAppData%\Programs\Python\Launcher\py.exe"

if not defined PY (
  echo   ERROR: Python is not installed or not on PATH.
  echo   Install it from https://www.python.org/downloads/ and tick
  echo   "Add Python to PATH" during setup, then run this again.
  echo.
  echo   If you just installed Python and this still fails, log off and
  echo   back on ^(or restart the computer^), then run this again - Windows
  echo   needs a fresh session to pick up some installs.
  echo.
  pause
  exit /b 1
)
for /f "delims=" %%v in ('"%PY%" --version 2^>^&1') do set "PYVER=%%v"
echo %PYVER% | findstr /C:"was not found" >nul
if not errorlevel 1 (
  echo   ERROR: Windows has a "python" shortcut on PATH, but no real Python is
  echo   installed - it just opens the Microsoft Store. Fix either way:
  echo     1^) Install Python from https://www.python.org/downloads/ and tick
  echo        "Add Python to PATH", then run this again. OR
  echo     2^) Go to Settings -^> Apps -^> Advanced app settings -^> App execution
  echo        aliases, turn OFF "python.exe" / "python3.exe", then install
  echo        Python from the link above and run this again.
  echo.
  pause
  exit /b 1
)
"%PY%" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
  echo   ERROR: Python is older than 3.10 ^(found %PYVER%^).
  echo   Install a newer version from https://www.python.org/downloads/ then run this again.
  echo.
  pause
  exit /b 1
)
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
