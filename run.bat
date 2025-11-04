@echo off
echo ========================================
echo Webtoon Downloader - Run from Source
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import customtkinter" 2>nul
if errorlevel 1 (
    echo Dependencies not found. Installing...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies OK!
)

echo.
echo Starting application...
echo.

REM Run the application
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Application crashed!
    pause
)
