"""
Add Meeting Management Tables

Run this script to add meeting-related tables to the database.
"""

from app import create_app, db
from app.models import Meeting, MeetingAgenda, MeetingNote, MeetingAttachment

def add_meeting_tables():
    """Add meeting management tables to database"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Creating meeting management tables...")
        
        try:
            # Create all tables
            db.create_all()
            print("✅ Meeting tables created successfully!")
            
            # Show created tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            meeting_tables = [t for t in tables if 'meeting' in t.lower()]
            print(f"\n📋 Meeting-related tables:")
            for table in meeting_tables:
                print(f"   - {table}")
            
            print("\n✨ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_meeting_tables()
