@echo off
echo ============================================
echo WeatherBot API Key Setup
echo ============================================
echo.
echo This script will set up your WeatherAPI key.
echo.
echo For evaluation purposes, use this key:
echo 309d537f8f4d4b5c8a9192738252411
echo.
echo.

set /p API_KEY="Enter your WeatherAPI key (or press Enter to use default): "

if "%API_KEY%"=="" (
    set API_KEY=309d537f8f4d4b5c8a9192738252411
    echo Using default evaluation key...
)

echo.
echo Setting environment variable...
setx WEATHERAPI_KEY "%API_KEY%"

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo The API key has been set for future sessions.
echo.
echo IMPORTANT: You must close and reopen your terminal
echo for the changes to take effect.
echo.
echo To verify, open a NEW terminal and run:
echo   echo %%WEATHERAPI_KEY%%
echo.
echo For this current session, the key is also set temporarily.
set WEATHERAPI_KEY=%API_KEY%
echo.

echo Testing API connection...
python -c "import os, requests; key=os.environ.get('WEATHERAPI_KEY', '%API_KEY%'); r=requests.get(f'http://api.weatherapi.com/v1/current.json?key={key}&q=London'); print('✓ API Working!' if r.status_code==200 else f'✗ API Error: {r.status_code}')" 2>nul

if errorlevel 1 (
    echo.
    echo Note: Python test failed. This is okay if Python isn't in PATH.
    echo The key is still set correctly.
)

echo.
pause
