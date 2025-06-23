@echo off
echo Starting Dinexor...

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo Error: requirements.txt not found. Please ensure it is in the same directory.
    pause
    exit /b 1
)

REM Check if Python is installed
where python
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH. Please install Python 3.6 or later.
    pause
    exit /b 1
)

REM Attempt to install dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Dependency installation failed. Please check for errors or install manually.
    pause
    exit /b 1
)

echo Dependencies installed successfully.

REM Launch the application
echo Launching Dinexor...
"C:\PyTools\Dinexor\directory_mapper.py" directory_mapper.py  # Replace with your actual Python path
pause