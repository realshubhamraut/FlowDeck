"""
Add delivery status fields to messages table
Run this script to update the database schema
"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if columns exist
        result = db.session.execute(text("PRAGMA table_info(messages)"))
        columns = [row[1] for row in result.fetchall()]
        
        # Add is_delivered column if it doesn't exist
        if 'is_delivered' not in columns:
            db.session.execute(text("""
                ALTER TABLE messages 
                ADD COLUMN is_delivered BOOLEAN DEFAULT 0
            """))
            print("✅ Added is_delivered column to messages table")
        else:
            print("ℹ️  is_delivered column already exists")
        
        # Add delivered_at column if it doesn't exist
        if 'delivered_at' not in columns:
            db.session.execute(text("""
                ALTER TABLE messages 
                ADD COLUMN delivered_at DATETIME
            """))
            print("✅ Added delivered_at column to messages table")
        else:
            print("ℹ️  delivered_at column already exists")
        
        db.session.commit()
        print("\n🎉 Database migration completed successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error during migration: {str(e)}")
        raise
