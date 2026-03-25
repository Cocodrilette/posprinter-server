@echo off
setlocal
cd /d "%~dp0"

echo [POS PRINTER] Starting Server...

:: Check for virtual environment
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
) else (
    set PYTHON_EXE=python
)

:: Run the server in a new minimized window
start "POS Printer Server" /min "%PYTHON_EXE%" server.py

:: Give it a few seconds to start
timeout /t 3 /nobreak > nul

:: Open the browser
start http://localhost:8000

echo [POS PRINTER] Server is running at http://localhost:8000
timeout /t 5
exit
