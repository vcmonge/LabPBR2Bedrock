@echo off
setlocal

set "APP_DIR=%~dp0"
set "SETUP_SCRIPT=%APP_DIR%scripts\windows_setup.ps1"

if not exist "%SETUP_SCRIPT%" goto missing_script

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SETUP_SCRIPT%"
set "SETUP_EXIT=%ERRORLEVEL%"

echo.
pause
exit /b %SETUP_EXIT%

:missing_script
echo Unable to find scripts\windows_setup.ps1 next to windows_setup.bat.
pause
exit /b 1
