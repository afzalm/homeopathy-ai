@echo off
REM Simple startup script for Homeopathy AI on Windows

echo.
echo 🏥 Starting Homeopathy AI API...
echo.
echo Checking dependencies...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt

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
