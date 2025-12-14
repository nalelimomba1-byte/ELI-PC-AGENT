@echo off
echo ╔═══════════════════════════════════════════════════════════╗
echo ║              Starting ELI AI Assistant                   ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo [1/2] Starting backend...
start "ELI Backend" python start_eli.py

echo [2/2] Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo [3/3] Opening ELI interface...
python eli_app.py

echo.
echo ELI has been closed.
pause
