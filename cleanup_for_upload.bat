@echo off
REM WeatherBot Cleanup Script - Reduces project size for upload

echo ============================================
echo WeatherBot Project Size Reduction
echo ============================================
echo.

REM Keep only the latest model
echo [1/5] Cleaning old models (keeping latest only)...
cd models
for /f "skip=1 delims=" %%f in ('dir /b /o-d *.tar.gz') do (
    echo Deleting: %%f
    del "%%f"
)
cd ..
echo Done! Kept only the latest model.
echo.

REM Remove Rasa cache
echo [2/5] Removing Rasa cache (.rasa folder)...
if exist .rasa (
    rmdir /s /q .rasa
    echo Done! Removed .rasa cache (364 MB saved)
) else (
    echo .rasa folder not found, skipping...
)
echo.

REM Remove pytest cache
echo [3/5] Removing pytest cache...
if exist .pytest_cache (
    rmdir /s /q .pytest_cache
    echo Done!
) else (
    echo .pytest_cache not found, skipping...
)
echo.

REM Remove Python cache files
echo [4/5] Removing Python cache files (__pycache__)...
for /d /r %%d in (__pycache__) do (
    if exist "%%d" (
        echo Removing: %%d
        rmdir /s /q "%%d"
    )
)
echo Done!
echo.

REM Remove test results
echo [5/5] Removing test results...
if exist results (
    rmdir /s /q results
    echo Done!
) else (
    echo results folder not found, skipping...
)
echo.

echo ============================================
echo Cleanup Complete!
echo ============================================
echo.
echo Size saved:
echo - Old models: ~450 MB
echo - Rasa cache: ~364 MB
echo - Other caches: ~10 MB
echo Total saved: ~824 MB
echo.
echo Current project size should be around 25-30 MB
echo (excluding .git folder)
echo.
pause
