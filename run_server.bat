@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at .venv
    echo Create it with: py -m venv .venv
    echo Then install deps with: .venv\Scripts\python.exe -m pip install -r requirements.txt
    exit /b 1
)

if "%PORT%"=="" set PORT=8000

call ".venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1

uvicorn app.main:app --host 127.0.0.1 --port %PORT% --reload
