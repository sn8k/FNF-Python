@echo off
echo Enter Venv
call .venv\scripts\activate
echo Installing dependencies...
call pip install -r requirements.txt
echo Dependencies installed.
echo.
echo starting game...
python main.py
echo.
echo game closed.
timeout 5
