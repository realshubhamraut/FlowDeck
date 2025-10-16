"""
Complete Database Schema Fix - Recreate notifications table
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
    
    if table_exists:
        print("⚠️  Notifications table exists. Checking schema...")
        
        # Get current schema
        cursor.execute("PRAGMA table_info(notifications)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"📋 Current columns: {column_names}")
        
        if 'message' not in column_names:
            print("\n🔧 Dropping and recreating notifications table with correct schema...")
            
            # Drop the old table
            cursor.execute("DROP TABLE IF EXISTS notifications")
            print("✅ Old table dropped")
    
    # Create table with correct schema
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
    
    # Create index on created_at for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)")
    
    print("✅ Notifications table created successfully!")
    
    # Verify the schema
    cursor.execute("PRAGMA table_info(notifications)")
    columns = cursor.fetchall()
    print("\n📋 Final notifications table schema:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Commit changes
    conn.commit()
    print("\n✅ Database schema fix completed successfully!")
    
except sqlite3.Error as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
