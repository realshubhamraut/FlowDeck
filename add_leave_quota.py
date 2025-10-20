"""
Database migration script to add leave quota fields to User model
"""

from app import create_app, db
import sqlite3

def add_leave_quota_fields():
    """Add leave quota related columns to users table"""
    app = create_app()
    
    with app.app_context():
        db_path = 'instance/flowdeck.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        columns_to_add = {
            'annual_leave_quota': 'INTEGER DEFAULT 0',
            'sick_leave_quota': 'INTEGER DEFAULT 0',
            'personal_leave_quota': 'INTEGER DEFAULT 0',
            'leave_quota_set_by_id': 'INTEGER'
        }
        
        for column_name, column_type in columns_to_add.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
                    conn.commit()
                    print(f'✅ Added {column_name} column to users table')
                except Exception as e:
                    print(f'❌ Error adding {column_name}: {str(e)}')
            else:
                print(f'ℹ️  Column {column_name} already exists')
        
        conn.close()
        print('🎉 Database migration completed successfully!')

if __name__ == '__main__':
    add_leave_quota_fields()
