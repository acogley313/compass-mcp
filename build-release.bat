@echo off
REM Create a release zip file (flat structure), excluding credentials and build artifacts
REM Usage: build-release.bat [version]
REM Example: build-release.bat 2.0.0
REM
REM Creates a flat zip structure for easy unzipping directly into existing installation:
REM   server.py
REM   compass_client.py
REM   exporter.py
REM   [etc - no root folder]

setlocal enabledelayedexpansion

set VERSION=%1
if "%VERSION%"=="" set VERSION=development

set RELEASE_NAME=compass-mcp-%VERSION%
set RELEASE_ZIP=%RELEASE_NAME%.zip
set DIST_DIR=dist

REM Create dist folder if it doesn't exist
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

echo Creating release: %RELEASE_NAME%

REM Check PowerShell availability
where powershell >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: PowerShell not found. Please install PowerShell or use 7-Zip manually.
    exit /b 1
)

echo Creating zip archive (flat structure)...

REM Use PowerShell to create flat zip with exclusions
powershell -NoProfile -Command "^
  $SourcePath = '%CD%'; ^
  $ZipPath = '%CD%\%DIST_DIR%\%RELEASE_ZIP%'; ^
  $Files = Get-ChildItem -Recurse -Path $SourcePath -File | ^
    Where-Object { ^
      -not ($_.FullName -like '*\.git*') -and ^
      -not ($_.FullName -like '*\.venv*') -and ^
      -not ($_.FullName -like '*\.ionapi') -and ^
      -not ($_.FullName -like '*\.pyc') -and ^
      -not ($_.FullName -like '*__pycache__*') -and ^
      -not ($_.FullName -like '*\.idea*') -and ^
      -not ($_.FullName -like '*\.iml') -and ^
      -not ($_.FullName -like '*\.zip') -and ^
      -not ($_.FullName -like '*dist\*') -and ^
      -not ($_.FullName -like '*build\*') -and ^
      -not ($_.FullName -like '*.claude\settings.local.json') -and ^
      -not ($_.FullName -like '*\.DS_Store') -and ^
      -not ($_.FullName -like '*\.egg-info*') ^
    }; ^
  Add-Type -AssemblyName 'System.IO.Compression.FileSystem'; ^
  if (Test-Path $ZipPath) { Remove-Item $ZipPath }; ^
  [IO.Compression.ZipFile]::CreateFromDirectory($SourcePath, $ZipPath, [IO.Compression.CompressionLevel]::Optimal, $false); ^
  Write-Host 'Zip created successfully'
"

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create zip file
    exit /b 1
)

echo.
echo Release created: %DIST_DIR%\%RELEASE_ZIP%
dir "%DIST_DIR%\%RELEASE_ZIP%"
echo.
echo Next steps:
echo   1. Review the zip file: %DIST_DIR%\%RELEASE_ZIP%
echo   2. Create a GitHub Release and upload the zip
echo   3. Share the download link with users
echo.
echo Users can extract with:
echo   tar -xf %RELEASE_ZIP% -C %%USERPROFILE%%\compass-mcp
echo   or unzip %RELEASE_ZIP% -d %%USERPROFILE%%\compass-mcp

endlocal
