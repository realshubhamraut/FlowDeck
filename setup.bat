@echo off
REM FlowDeck Setup Script for Windows

echo ================================
echo    FlowDeck Setup Script
echo ================================
echo.

REM Check Python version
echo Checking Python version...
python --version

if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
)

echo + Python is installed
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo X Failed to create virtual environment
    exit /b 1
)

echo + Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo X Failed to install dependencies
    exit /b 1
)

echo + Dependencies installed
echo.

REM Create .env file
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo + .env file created (please configure it with your settings)
) else (
    echo i .env file already exists
)
echo.

REM Initialize database
echo Initializing database...
python run.py init-db

if errorlevel 1 (
    echo X Failed to initialize database
    exit /b 1
)

echo + Database initialized
echo.

REM Seed database
echo Seeding database with demo data...
python run.py seed

if errorlevel 1 (
    echo X Failed to seed database
    exit /b 1
)

echo + Database seeded
echo.

REM Success message
echo ================================
echo    + Setup Complete!
echo ================================
echo.
echo Default login credentials:
echo   Email: admin@flowdeck.org
echo   Password: admin123
echo.
echo WARNING: Remember to:
echo   1. Edit .env file with your configuration
echo   2. Change the default admin password
echo   3. Configure email settings
echo   4. Add API keys (OpenAI, Google Calendar, etc.)
echo.
echo To start the application:
echo   venv\Scripts\activate.bat
echo   python run.py
echo.
echo The application will be available at:
echo   http://localhost:5000
echo.
pause
