#!/bin/bash

echo "================================"
echo "   FlowDeck Setup (Python 3.13)"
echo "================================"
echo ""

# Step 1: Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi
echo "✅ Virtual environment created"
echo ""

# Step 2: Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Step 3: Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✅ Pip upgraded"
echo ""

# Step 4: Install packages one by one for better error handling
echo "📚 Installing dependencies (this may take a few minutes)..."

# Core Flask packages
echo "  Installing Flask core..."
pip install Flask==3.0.3 Werkzeug==3.0.3

echo "  Installing Flask extensions..."
pip install Flask-SQLAlchemy==3.1.1 SQLAlchemy==2.0.35
pip install Flask-Login==0.6.3
pip install Flask-Mail==0.10.0
pip install Flask-WTF==1.2.1 WTForms==3.1.2
pip install Flask-Migrate==4.0.7

echo "  Installing Socket.IO..."
pip install python-socketio==5.11.2 python-engineio==4.9.1
pip install Flask-SocketIO==5.3.6
pip install eventlet==0.36.1

echo "  Installing utilities..."
pip install python-dotenv==1.0.1
pip install email-validator==2.2.0
pip install Pillow==10.4.0
pip install requests==2.32.3
pip install python-dateutil==2.9.0
pip install click==8.1.7
pip install itsdangerous==2.2.0
pip install greenlet==3.0.3
pip install dnspython==2.6.1

echo "  Installing optional packages..."
pip install gunicorn==22.0.0
pip install PyJWT==2.9.0
pip install bleach==6.1.0
pip install markdown==3.6

# Install AI and external services (may fail on some systems)
echo "  Installing AI/API packages (optional, may skip if errors)..."
pip install openai==1.40.0 || echo "⚠️  OpenAI skipped"
pip install google-auth==2.32.0 google-auth-oauthlib==1.2.1 google-auth-httplib2==0.2.0 google-api-python-client==2.140.0 || echo "⚠️  Google APIs skipped"
pip install sendgrid==6.11.0 || echo "⚠️  SendGrid skipped"
pip install redis==5.0.8 || echo "⚠️  Redis skipped"
pip install celery==5.4.0 || echo "⚠️  Celery skipped"

echo "✅ Dependencies installed"
echo ""

# Step 5: Create .env file
echo "📝 Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env file created from template"
else
    echo "⚠️  .env file already exists, skipping"
fi
echo ""

# Step 6: Initialize database
echo "🗄️  Initializing database..."
python run.py init-db
if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize database"
    exit 1
fi
echo "✅ Database initialized"
echo ""

# Step 7: Seed database
echo "🌱 Seeding database with demo data..."
python run.py seed
if [ $? -ne 0 ]; then
    echo "❌ Failed to seed database"
    exit 1
fi
echo "✅ Database seeded"
echo ""

echo "================================"
echo "   ✅ Setup Complete!"
echo "================================"
echo ""
echo "🎉 FlowDeck is ready to use!"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the app: python run.py"
echo "  3. Open browser: http://localhost:5000"
echo ""
echo "📧 Default credentials:"
echo "  Email:    admin@flowdeck.org"
echo "  Password: admin123"
echo ""
echo "⚠️  IMPORTANT: Change the default password after first login!"
echo ""
