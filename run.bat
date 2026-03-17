@echo off
REM Simple startup script for Homeopathy AI on Windows

echo.
echo 🏥 Starting Homeopathy AI API...
echo.

REM Try to find Python
set PYTHON_CMD=
for /f "delims=" %%i in ('where python 2^>nul') do set PYTHON_CMD=%%i
if "%PYTHON_CMD%"=="" (
    for /f "delims=" %%i in ('where python3 2^>nul') do set PYTHON_CMD=%%i
)
if "%PYTHON_CMD%"=="" (
    for /f "delims=" %%i in ('where py 2^>nul') do set PYTHON_CMD=%%i
)

if "%PYTHON_CMD%"=="" (
    echo ❌ Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo ✅ Found Python: %PYTHON_CMD%
echo.

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo 📦 Creating virtual environment...
    "%PYTHON_CMD%" -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo ✅ .env created. Please update it with your configuration.
)

echo.
echo ✅ Setup complete!
echo.
echo 🚀 Starting server on http://localhost:8000
echo 📖 API docs available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
