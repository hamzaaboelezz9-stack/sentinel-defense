@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
%PY% -c "import sys;assert sys.version_info >= (3,12)" >nul 2>nul
if errorlevel 1 (echo Install Python 3.12 or newer and enable Add Python to PATH. & pause & exit /b 1)
if not exist .venv\Scripts\python.exe %PY% -m venv .venv
if errorlevel 1 (echo Could not create Python environment. Check folder permissions. & pause & exit /b 1)
if not exist .venv\requirements.installed goto install
fc /b backend\requirements.lock .venv\requirements.installed >nul 2>nul
if errorlevel 1 goto install
goto launch
:install
.venv\Scripts\python.exe -m pip install -r backend\requirements.lock
if errorlevel 1 (echo Dependency installation failed. Check network, disk space, and the pip error above. & pause & exit /b 1)
copy /y backend\requirements.lock .venv\requirements.installed >nul
:launch
echo Open http://127.0.0.1:8000 after startup. A NEW database gets credentials printed below.
.venv\Scripts\python.exe scripts\run.py
if errorlevel 1 echo Startup failed. Check port 8000 or set PORT to another local port.
pause
