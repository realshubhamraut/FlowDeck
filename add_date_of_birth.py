"""
Migration script to add date_of_birth field to users table
"""
import sqlite3
from datetime import datetime

def migrate():
    """Add date_of_birth column to users table"""
    conn = sqlite3.connect('instance/flowdeck.db')
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'date_of_birth' not in columns:
            print("Adding date_of_birth column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN date_of_birth DATE")
            conn.commit()
            print("✅ Successfully added date_of_birth column!")
        else:
            print("✅ date_of_birth column already exists!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
