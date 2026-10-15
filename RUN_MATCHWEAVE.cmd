@echo off
setlocal
cd /d "%~dp0"
title MatchWeave AI
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-local.ps1"
if errorlevel 1 (
  echo.
  echo MatchWeave could not start. Read the error above and START_HERE.txt.
  pause
)
endlocal
