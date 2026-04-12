@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build.ps1" -Configuration release %*
exit /b %ERRORLEVEL%
