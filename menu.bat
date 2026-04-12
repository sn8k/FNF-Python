@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_CMD=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
)

:menu
cls
echo ========================================
echo  FNF-Python - Menu de lancement
echo ========================================
echo.
echo  1. Lancer le jeu
echo  2. Ouvrir le Chart Editor
echo  3. Voir les derniers logs
echo  4. Quitter
echo.
set /p "CHOICE=Choix: "

if "%CHOICE%"=="1" goto run_game
if "%CHOICE%"=="2" goto run_chart_editor
if "%CHOICE%"=="3" goto show_logs
if "%CHOICE%"=="4" goto end

echo.
echo Choix invalide.
pause
goto menu

:run_game
cls
echo Lancement du jeu...
"%PYTHON_CMD%" main.py
echo.
echo Jeu ferme.
pause
goto menu

:run_chart_editor
cls
echo Lancement du Chart Editor...
"%PYTHON_CMD%" -m src.chart_editor
echo.
echo Chart Editor ferme.
pause
goto menu

:show_logs
cls
echo ========================================
echo  Derniers logs utilisateur
echo ========================================
if exist "logs\user.log" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Content -LiteralPath 'logs\user.log' -Tail 80"
) else (
    echo Aucun fichier logs\user.log trouve.
)
echo.
echo ========================================
echo  Derniers logs debug
echo ========================================
if exist "logs\debug.log" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Content -LiteralPath 'logs\debug.log' -Tail 80"
) else (
    echo Aucun fichier logs\debug.log trouve.
)
echo.
pause
goto menu

:end
endlocal
