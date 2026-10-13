@echo off
setlocal

set "APP_DIR=%~dp0"
set "VENV_PYTHONW=%APP_DIR%.venv\Scripts\pythonw.exe"

if not exist "%VENV_PYTHONW%" goto launch_error

start "" /D "%APP_DIR%" "%VENV_PYTHONW%" "%APP_DIR%app.py"
if errorlevel 1 goto launch_error

exit /b 0

:launch_error
echo Unable to start the application because the virtual environment is missing.
echo Run windows_setup.bat to create the .venv environment and install the requirements.
pause
exit /b 1
