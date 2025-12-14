@echo off
echo Starting ELI in Debug Mode...
echo Output will be saved to jarvis_debug.log
python run_jarvis.py > jarvis_debug.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error occurred! Check jarvis_debug.log for details.
    pause
)
