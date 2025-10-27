@echo off
setlocal enableextensions enabledelayedexpansion
REM WeatherBot Launcher - Starts all required services reliably from any location

REM Resolve project directory to the folder of this script
set "PROJECT_DIR=%~dp0"
pushd "%PROJECT_DIR%" >nul

echo ========================================
echo   Starting WeatherBot Services
echo ========================================
echo.

REM Set conda paths (adjust if your Anaconda path is different)
set "CONDA_PATH=C:\Users\krish\anaconda3"
set "CONDA_ENV=weather_env"

REM Prefer direct env Python to avoid activation issues
set "ENV_PY=%CONDA_PATH%\envs\%CONDA_ENV%\python.exe"
if not exist "%ENV_PY%" (
	set "ENV_PY=%USERPROFILE%\anaconda3\envs\%CONDA_ENV%\python.exe"
)
if not exist "%ENV_PY%" (
	set "ENV_PY=%USERPROFILE%\miniconda3\envs\%CONDA_ENV%\python.exe"
)
if not exist "%ENV_PY%" (
	echo [error] Could not find Python for env %CONDA_ENV%.
	echo         Update CONDA_PATH/CONDA_ENV at the top of this file.
	pause
	exit /b 1
)

REM Optional: warn if WEATHERAPI_KEY is not set in the environment
if not defined WEATHERAPI_KEY (
	echo [info] WEATHERAPI_KEY not found in environment. If WeatherAPI calls fail, set it via ^"setx WEATHERAPI_KEY your_key^" and reopen windows.
)

echo [1/4] Installing Flask if needed...
"%ENV_PY%" -m pip install flask flask-cors --quiet

echo [2/4] Starting Rasa Action Server...
start "Rasa Actions" cmd /k cd /d "%PROJECT_DIR%" ^&^& "%ENV_PY%" -m rasa run actions
timeout /t 5 /nobreak >nul

echo [3/4] Starting Rasa Server...
start "Rasa Server" cmd /k cd /d "%PROJECT_DIR%" ^&^& "%ENV_PY%" -m rasa run --enable-api --cors * --port 5005 -i 0.0.0.0
timeout /t 10 /nobreak >nul

echo [4/4] Starting Web Interface...
start "WeatherBot Web" cmd /k cd /d "%PROJECT_DIR%" ^&^& "%ENV_PY%" web_server.py
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   WeatherBot is now running!
echo ========================================
echo.

REM Auto-detect the first non-localhost IPv4 address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set "DETECTED_IP=%%a"
    goto :ip_found
)
:ip_found
REM Trim leading spaces
set "DETECTED_IP=%DETECTED_IP: =%"

if defined DETECTED_IP (
    echo Web Interface: http://%DETECTED_IP%:8080
    echo Rasa API: http://%DETECTED_IP%:5005
    echo.
    echo Press any key to open the web interface...
    pause >nul
    start "" http://%DETECTED_IP%:8080
) else (
    echo Web Interface: http://127.0.0.1:8080
    echo Rasa API: http://127.0.0.1:5005
    echo.
    echo Press any key to open the web interface...
    pause >nul
    start "" http://127.0.0.1:8080
)

echo.
echo To stop all services, close all command windows.
echo.
pause
