#!/bin/bash

# FlowDeck Setup Script
echo "================================"
echo "   FlowDeck Setup Script"
echo "================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if Python version is compatible (3.9-3.12 recommended)
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  Warning: Python 3.13 detected. Some packages may have compatibility issues."
    echo "    If installation fails, consider using Python 3.11 or 3.12."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✓ Python is installed"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created (please configure it with your settings)"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Initialize database
echo "Initializing database..."
python run.py init-db

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize database"
    exit 1
fi

echo "✓ Database initialized"
echo ""

# Seed database
echo "Seeding database with demo data..."
python run.py seed

if [ $? -ne 0 ]; then
    echo "❌ Failed to seed database"
    exit 1
fi

echo "✓ Database seeded"
echo ""

# Success message
echo "================================"
echo "   ✅ Setup Complete!"
echo "================================"
echo ""
echo "Default login credentials:"
echo "  Email: admin@flowdeck.org"
echo "  Password: admin123"
echo ""
echo "⚠️  Remember to:"
echo "  1. Edit .env file with your configuration"
echo "  2. Change the default admin password"
echo "  3. Configure email settings"
echo "  4. Add API keys (OpenAI, Google Calendar, etc.)"
echo ""
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "The application will be available at:"
echo "  http://localhost:5000"
echo ""
