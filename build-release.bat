@echo off
REM Create a release zip file, excluding credentials and build artifacts
REM Usage: release.bat [version]
REM Example: release.bat 2.0.0

setlocal enabledelayedexpansion

set VERSION=%1
if "%VERSION%"=="" set VERSION=development

set RELEASE_NAME=compass-mcp-%VERSION%
set RELEASE_ZIP=%RELEASE_NAME%.zip
set DIST_DIR=dist

REM Create dist folder if it doesn't exist
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

echo Creating release: %RELEASE_NAME%

REM Check if 7-Zip is available (common on Windows)
where 7z >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: 7-Zip not found. Please install 7-Zip or use PowerShell to create the zip.
    echo.
    echo Alternative: Use PowerShell:
    echo   powershell -Command "Compress-Archive -Path . -DestinationPath '%RELEASE_ZIP%' -CompressionLevel Optimal"
    exit /b 1
)

REM Create a temporary directory
for /f %%A in ('powershell -Command "[System.IO.Path]::GetTempPath()"') do set TEMP_DIR=%%A
set RELEASE_DIR=%TEMP_DIR%compass-mcp-build

if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"

echo Copying files...

REM Copy all files except those in the exclusion list
for /r . %%F in (*) do (
    set FILE=%%F
    setlocal enabledelayedexpansion
    if not "!FILE!"=="!FILE:.ionapi=!" goto skip_copy
    if not "!FILE!"=="!FILE:.pyc=!" goto skip_copy
    if not "!FILE!"=="!FILE:.venv=!" goto skip_copy
    if not "!FILE!"=="!FILE:.git=!" goto skip_copy
    if not "!FILE!"=="!FILE:__pycache__=!" goto skip_copy
    if not "!FILE!"=="!FILE:.idea=!" goto skip_copy
    if not "!FILE!"=="!FILE:.iml=!" goto skip_copy

    REM Copy file while preserving directory structure
    set RELATIVE_PATH=%%F
    set RELATIVE_PATH=!RELATIVE_PATH:%CD%\=!
    mkdir "%RELEASE_DIR%\!RELATIVE_PATH:~0,-1!" 2>nul
    copy "%%F" "%RELEASE_DIR%\!RELATIVE_PATH!" >nul

    :skip_copy
    endlocal
)

echo Creating zip archive...

REM Create the zip using 7-Zip
cd "%TEMP_DIR%"
7z a -r "%RELEASE_ZIP%" "%RELEASE_NAME%" >nul
cd %CD%

REM Move to dist folder
move "%TEMP_DIR%%RELEASE_ZIP%" "%DIST_DIR%\%RELEASE_ZIP%" >nul 2>&1

REM Cleanup
rmdir /s /q "%RELEASE_DIR%"

echo.
echo Release created: %DIST_DIR%\%RELEASE_ZIP%
dir "%DIST_DIR%\%RELEASE_ZIP%"
echo.
echo Next steps:
echo   1. Review the zip file: %DIST_DIR%\%RELEASE_ZIP%
echo   2. Create a GitHub Release and upload the zip
echo   3. Share the download link with users

endlocal
