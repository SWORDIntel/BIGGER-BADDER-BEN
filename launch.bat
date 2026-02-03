@echo off
REM Atomic Clock Display Launcher for Windows
REM Launches the atomic clock application on Windows systems

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

set APP_NAME=Atomic Clock Display
set PYTHON_SCRIPT=atomic_clock.py

echo.
echo ===============================================================
echo   %APP_NAME%
echo ===============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python %PYTHON_VERSION% found

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found
    set /p CREATE_VENV="Create virtual environment? (y/n): "
    if /i "!CREATE_VENV!"=="y" (
        echo [INFO] Creating virtual environment...
        python -m venv venv
        call venv\Scripts\activate.bat
        echo [SUCCESS] Virtual environment created
    )
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
python -c "import ntplib" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Missing dependencies
    set /p INSTALL_DEPS="Install dependencies? (y/n): "
    if /i "!INSTALL_DEPS!"=="y" (
        echo [INFO] Installing dependencies...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [ERROR] Failed to install dependencies
            pause
            exit /b 1
        )
        echo [SUCCESS] Dependencies installed
    ) else (
        echo [ERROR] Cannot run without required dependencies
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] All dependencies installed
)

REM Check configuration
echo [INFO] Checking configuration...
if not exist "config\locations.json" (
    echo [ERROR] Configuration file not found: config\locations.json
    pause
    exit /b 1
)

REM Launch application
echo [INFO] Launching atomic clock...
echo.

python "%PYTHON_SCRIPT%" %*

if errorlevel 1 (
    echo [ERROR] Application exited with error
    pause
    exit /b 1
) else (
    echo [SUCCESS] Application exited successfully
)

endlocal
