@echo off
setlocal enableextensions enabledelayedexpansion
REM Debug Launcher - runs checks and logs outputs to help diagnose "files not opening"

set "PROJECT_DIR=%~dp0"
pushd "%PROJECT_DIR%" >nul

set "CONDA_PATH=C:\Users\krish\anaconda3"
set "CONDA_ENV=weather_env"

set "ENV_PY=%CONDA_PATH%\envs\%CONDA_ENV%\python.exe"
if not exist "%ENV_PY%" (
  set "ENV_PY=%USERPROFILE%\anaconda3\envs\%CONDA_ENV%\python.exe"
)
if not exist "%ENV_PY%" (
  set "ENV_PY=%USERPROFILE%\miniconda3\envs\%CONDA_ENV%\python.exe"
)
if not exist "%ENV_PY%" (
  echo [error] Could not find Python for env %CONDA_ENV%.
  echo        Update CONDA_PATH/CONDA_ENV in this file.
  pause
  exit /b 1
)

if not exist logs mkdir logs >nul 2>&1

echo [check] Project dir: %PROJECT_DIR%
echo [check] Writing logs under: %PROJECT_DIR%logs

echo [check] Verifying key files...
if not exist "web_server.py" echo [error] Missing web_server.py in %PROJECT_DIR% & goto :eof
if not exist "actions\actions.py" echo [error] Missing actions\actions.py in %PROJECT_DIR% & goto :eof

echo [check] Verifying Conda activate script...
if not exist "%CONDA_PATH%\Scripts\activate.bat" (
  echo [error] activate.bat not found at %CONDA_PATH%\Scripts\activate.bat
  echo        Adjust CONDA_PATH in this file to your Anaconda install.
  goto :eof
)

echo [step] Activating environment and capturing versions...
"%ENV_PY%" --version > logs\env.log 2>&1
"%ENV_PY%" -m rasa --version >> logs\env.log 2>&1
echo [ok] Versions written to logs\env.log

echo [step] Ensuring Flask is installed...
python -m pip install flask flask-cors --quiet

echo [step] Starting Action Server (logs\actions.log)...
start "Actions (logs\\actions.log)" cmd /k cd /d "%PROJECT_DIR%" ^&^& "%ENV_PY%" -m rasa run actions 1>>"logs\actions.log" 2>&1
timeout /t 5 /nobreak >nul

echo [step] Starting Rasa Server (logs\rasa.log)...
start "Rasa (logs\\rasa.log)" cmd /k cd /d "%PROJECT_DIR%" ^&^& "%ENV_PY%" -m rasa run --enable-api --cors * --port 5005 -i 0.0.0.0 1>>"logs\rasa.log" 2>&1
timeout /t 10 /nobreak >nul

echo [step] Starting Web Server (logs\web.log)...
start "Web (logs\\web.log)" cmd /k cd /d "%PROJECT_DIR%" ^&^& "%ENV_PY%" web_server.py 1>>"logs\web.log" 2>&1
timeout /t 3 /nobreak >nul

echo [ok] Launched. Opening browser...
start "" http://localhost:8080

echo.
echo If the page doesn't load, open the log files in the logs folder (actions.log, rasa.log, web.log) and share the last 30 lines.
echo Press any key to exit this debug launcher.
pause >nul

