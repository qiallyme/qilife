@echo off
echo Installing Dinexor dependencies...
if not exist requirements.txt (
    echo Error: requirements.txt not found. Please ensure it is in the same directory.
    pause
    exit /b 1
)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Installation failed. Please check for errors.
    pause
    exit /b 1
)
echo Installation complete. Press any key to continue.
pause