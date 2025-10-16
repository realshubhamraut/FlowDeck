"""
Fix Database Schema - Add missing 'message' column to notifications table
"""
import sqlite3
import os

# Path to database
db_path = 'flowdeck.db'

if not os.path.exists(db_path):
    print(f"❌ Database file not found: {db_path}")
    exit(1)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if notifications table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("❌ Notifications table doesn't exist!")
        print("Creating notifications table with correct schema...")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                notification_type VARCHAR(50),
                task_id INTEGER,
                message_id INTEGER,
                action_url VARCHAR(500),
                is_read BOOLEAN DEFAULT 0,
                read_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
            )
        ''')
        print("✅ Notifications table created successfully!")
    else:
        # Check current schema
        cursor.execute("PRAGMA table_info(notifications)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📋 Current notifications table columns: {column_names}")
        
        # Check if 'message' column exists
        if 'message' not in column_names:
            print("⚠️  'message' column is missing!")
            print("Adding 'message' column to notifications table...")
            
            # Add the missing column
            cursor.execute("ALTER TABLE notifications ADD COLUMN message TEXT NOT NULL DEFAULT ''")
            
            print("✅ 'message' column added successfully!")
        else:
            print("✅ 'message' column already exists!")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(notifications)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"\n📋 Updated notifications table columns: {column_names}")
    
    # Commit changes
    conn.commit()
    print("\n✅ Database schema fix completed successfully!")
    
except sqlite3.Error as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
