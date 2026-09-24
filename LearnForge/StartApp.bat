@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
  echo Virtual env not found at .venv. Create it with: uv sync
  exit /b 1
)

call .venv\Scripts\activate.bat
python UI\HomePage.py
endlocal
