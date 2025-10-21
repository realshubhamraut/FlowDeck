"""
Complete Database Initialization Script
Creates all tables from models and seeds with initial data
"""

import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import *  # Import all models
from app.database import init_database_features
from app.utils.seed import seed_database

def init_complete_database():
    """Initialize complete database with all tables and seed data"""
    
    app = create_app()
    
    with app.app_context():
        print("\n🔧 Initializing FlowDeck Database...")
        print("=" * 60)
        
        # Drop all tables first (fresh start)
        print("\n1. Dropping existing tables...")
        db.drop_all()
        print("   ✓ All existing tables dropped")
        
        # Create all tables from models
        print("\n2. Creating tables from models...")
        db.create_all()
        print("   ✓ All tables created")
        
        # Initialize database features (triggers, views, indexes)
        print("\n3. Initializing database features...")
        init_database_features(app)
        print("   ✓ Database features initialized")
        
        # Commit to ensure everything is written
        db.session.commit()
        
        # Verify tables were created
        print("\n4. Verifying tables...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"   ✓ {len(tables)} tables created:")
        for table in sorted(tables):
            print(f"      - {table}")
        
        # Verify notifications table has message column
        if 'notifications' in tables:
            columns = [col['name'] for col in inspector.get_columns('notifications')]
            if 'message' in columns:
                print("\n  SUCCESS: notifications table has 'message' column!")
            else:
                print("\n  ERROR: notifications table missing 'message' column!")
                print(f"      Columns found: {columns}")
                return False
        
        # Seed database with initial data
        print("\n5. Seeding database with initial data...")
        seed_database()
        
        print("\n" + "=" * 60)
        print("Database initialization completed successfully!")
        print("\nDemo Login Credentials:")
        print("Email: admin@flowdeck.org")
        print("Password: admin123")
        print("\n Remember to change the default password in production!")
        print("=" * 60 + "\n")
        
        return True

if __name__ == '__main__':
    success = init_complete_database()
    sys.exit(0 if success else 1)
