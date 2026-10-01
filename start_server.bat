@echo off
setlocal
cd /d "%~dp0"

echo [POS PRINTER] Starting Server...

set WEB_PORT=8000
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if "%%A"=="WEB_PORT" set WEB_PORT=%%~B
    )
)

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
start http://localhost:%WEB_PORT%

echo [POS PRINTER] Server is running at http://localhost:%WEB_PORT%
timeout /t 5
exit
