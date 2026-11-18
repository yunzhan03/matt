@echo off
rem One-command entry for the Cursor <-> Magpie bridge.
rem   tools\bridge.cmd          diagnose, repair if broken, re-check
rem   tools\bridge.cmd check    diagnose only, touch nothing
setlocal
set "SCRIPT=%~dp0cursor-bridge-check.ps1"

if /I "%~1"=="check" goto :check
if /I "%~1"=="--check" goto :check
goto :recover

:check
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%"
exit /b %ERRORLEVEL%

:recover
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -Fix
exit /b %ERRORLEVEL%
