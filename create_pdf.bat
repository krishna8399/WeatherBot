@echo off
echo Installing required packages...
C:\Users\krish\anaconda3\envs\weather_env\python.exe -m pip install playwright
echo.
echo Installing Chromium browser...
C:\Users\krish\anaconda3\envs\weather_env\python.exe -m playwright install chromium
echo.
echo Converting presentation to PDF...
C:\Users\krish\anaconda3\envs\weather_env\python.exe convert_to_pdf.py
echo.
echo Done! Check presentation.pdf
pause
