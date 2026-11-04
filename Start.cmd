@echo off
cd /d "%~dp0"
if not exist .tmp mkdir .tmp
set "TEMP=%CD%\.tmp"
set "TMP=%TEMP%"
if not exist .venv\Scripts\python.exe (
  python -m venv .venv
  if errorlevel 1 goto error
)
.venv\Scripts\python.exe -m pip --version >nul 2>&1
if errorlevel 1 (
  .venv\Scripts\python.exe -m ensurepip --upgrade
  if errorlevel 1 goto error
)
.venv\Scripts\python.exe -c "import yt_dlp, static_ffmpeg" >nul 2>&1
if errorlevel 1 (
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto error
)
start "" .venv\Scripts\pythonw.exe app.py
exit /b
:error
echo Setup failed. Check your internet connection and Python installation.
pause
