@echo off
REM Friday Night Funkin' Lightweight - Installation Script
REM This script sets up the game environment

echo.
echo ========================================
echo FNF Lightweight - Setup Installation
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher from python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Try installing pygame with wheels first
echo Installing pygame...
python -m pip install pygame==2.5.0 --upgrade

if %errorlevel% neq 0 (
    echo.
    echo WARNING: pygame installation failed!
    echo Attempting alternative installation method...
    python -m pip install --upgrade --user pygame
)

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Could not install pygame.
    echo.
    echo Try these alternatives:
    echo 1. Install Anaconda from https://www.anaconda.com/download and run: conda install pygame
    echo 2. Use official Python from https://www.python.org and run: pip install pygame
    echo 3. Check your internet connection and firewall settings
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo You can now run the game with:
echo     python main.py
echo.
echo Or create custom charts with:
echo     python -m src.chart_editor
echo.
pause
