@echo off
REM WeatherBot Launcher - Starts all required services

echo ========================================
echo   Starting WeatherBot Services
echo ========================================
echo.

REM Set conda paths
set CONDA_PATH=C:\Users\krish\anaconda3
set CONDA_ENV=weather_env

echo [1/4] Installing Flask if needed...
%CONDA_PATH%\envs\%CONDA_ENV%\python.exe -m pip install flask flask-cors --quiet

echo [2/4] Starting Rasa Action Server...
start "Rasa Actions" cmd /k "%CONDA_PATH%\Scripts\activate.bat %CONDA_ENV% && rasa run actions"
timeout /t 5 /nobreak >nul

echo [3/4] Starting Rasa Server...
start "Rasa Server" cmd /k "%CONDA_PATH%\Scripts\activate.bat %CONDA_ENV% && rasa run --enable-api --cors * --port 5005"
timeout /t 10 /nobreak >nul

echo [4/4] Starting Web Interface...
start "WeatherBot Web" cmd /k "%CONDA_PATH%\Scripts\activate.bat %CONDA_ENV% && python web_server.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   WeatherBot is now running!
echo ========================================
echo.
echo Web Interface: http://localhost:8080
echo Rasa API: http://localhost:5005
echo.
echo To share with others on your network:
echo 1. Find your IP: ipconfig (look for IPv4 Address)
echo 2. Share: http://YOUR_IP:8080
echo.
echo Press any key to open the web interface...
pause >nul

start http://localhost:8080

echo.
echo To stop all services, close all command windows.
echo.
pause
