@echo off
setlocal
cd /d "%~dp0"

echo [POS PRINTER] Preparing for build...

:: Check for virtual environment
if exist ".venv\Scripts\python.exe" (
    set PY_ENV=.venv\Scripts\python.exe
    set PYI_ENV=.venv\Scripts\pyinstaller.exe
) else (
    set PY_ENV=python
    set PYI_ENV=pyinstaller
)

echo [POS PRINTER] Installing/Updating PyInstaller...
"%PY_ENV%" -m pip install pyinstaller --quiet

echo [POS PRINTER] Cleaning old build files...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist *.spec del *.spec

echo [POS PRINTER] Building EXE (This may take a minute)...
:: Notes:
:: --onefile: Creates a single executable.
:: --console: Keep the console open for logs as requested.
:: --add-data: Includes the necessary folders.
:: --hidden-import: For modules PyInstaller might miss.
"%PYI_ENV%" ^
    --noconfirm ^
    --onefile ^
    --console ^
    --name "POSPrinterServer_v1.0" ^
    --add-data "templates;templates" ^
    --add-data "frontend/dist;frontend/dist" ^
    --add-data ".venv/Lib/site-packages/escpos;escpos" ^
    --hidden-import uvicorn.logging ^
    --hidden-import uvicorn.loops ^
    --hidden-import uvicorn.loops.auto ^
    --hidden-import uvicorn.protocols ^
    --hidden-import uvicorn.protocols.http ^
    --hidden-import uvicorn.protocols.http.auto ^
    --hidden-import uvicorn.protocols.websockets ^
    --hidden-import uvicorn.protocols.websockets.auto ^
    --hidden-import uvicorn.lifespan ^
    --hidden-import uvicorn.lifespan.on ^
    --hidden-import uvicorn.lifespan.off ^
    --hidden-import uvicorn.lifespan.auto ^
    --hidden-import email.mime.multipart ^
    --hidden-import email.mime.text ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [POS PRINTER] Success! Executable created in 'dist' folder.
echo [POS PRINTER] Filename: dist\POSPrinterServer_v1.0.exe
echo.
pause
