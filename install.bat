@echo off
echo ========================================
echo System Monitor Pro - Glassmorphism Edition
echo Installation Script
echo ========================================
echo.

echo Checking Python...
python --version || (
    echo Python 3.7+ required
    pause
    exit /b 1
)
echo Python found
echo.

echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo Installation complete!
    echo.
    echo Run with: python system_monitor_glass.py
    echo Or use: run.bat
) else (
    echo Installation failed
    pause
    exit /b 1
)
pause
