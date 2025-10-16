"""
Database initialization with triggers, functions, and views
SQLite advanced features implementation
"""

from app import db
from sqlalchemy import event, text
from app.models import Task, User, AnalyticsReport, AuditLog


def init_database_features(app):
    """Initialize database triggers, functions, and views"""
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create triggers
        create_triggers()
        
        # Create views
        create_views()
        
        # Create indexes
        create_indexes()
        
        print("Database initialized with advanced features")


def create_triggers():
    """Create database triggers"""
    
    # Trigger 1: Auto-update analytics when task is completed
    trigger_task_completion = """
    CREATE TRIGGER IF NOT EXISTS update_analytics_on_task_completion
    AFTER UPDATE OF status ON tasks
    WHEN NEW.status = 'done' AND OLD.status != 'done'
    BEGIN
        -- This trigger fires when a task is marked as done
        UPDATE tasks SET completed_date = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    """
    
    # Trigger 2: Log audit entry when user is created
    trigger_user_creation = """
    CREATE TRIGGER IF NOT EXISTS log_user_creation
    AFTER INSERT ON users
    BEGIN
        INSERT INTO audit_logs (
            user_id, organisation_id, action, entity_type, entity_id, 
            new_value, created_at
        ) VALUES (
            NEW.id, NEW.organisation_id, 'user_created', 'User', NEW.id,
            'User created: ' || NEW.email, CURRENT_TIMESTAMP
        );
    END;
    """
    
    # Trigger 3: Update task updated_at timestamp
    trigger_task_update = """
    CREATE TRIGGER IF NOT EXISTS update_task_timestamp
    AFTER UPDATE ON tasks
    BEGIN
        UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    """
    
    # Trigger 4: Auto-calculate task actual hours from time logs
    trigger_time_log = """
    CREATE TRIGGER IF NOT EXISTS update_task_hours_on_time_log
    AFTER INSERT ON time_logs
    BEGIN
        UPDATE tasks 
        SET actual_hours = (
            SELECT COALESCE(SUM(duration), 0) 
            FROM time_logs 
            WHERE task_id = NEW.task_id
        )
        WHERE id = NEW.task_id;
    END;
    """
    
    # Trigger 5: Create notification when task is assigned
    trigger_task_assignment = """
    CREATE TRIGGER IF NOT EXISTS notify_task_assignment
    AFTER INSERT ON task_assignees
    BEGIN
        INSERT INTO notifications (
            user_id, title, message, notification_type, task_id, 
            action_url, created_at
        )
        SELECT 
            NEW.user_id,
            'New Task Assigned',
            'You have been assigned to: ' || t.title,
            'task_assigned',
            NEW.task_id,
            '/tasks/' || NEW.task_id,
            CURRENT_TIMESTAMP
        FROM tasks t WHERE t.id = NEW.task_id;
    END;
    """
    
    try:
        db.session.execute(text(trigger_task_completion))
        db.session.execute(text(trigger_user_creation))
        db.session.execute(text(trigger_task_update))
        db.session.execute(text(trigger_time_log))
        db.session.execute(text(trigger_task_assignment))
        db.session.commit()
        print("✓ Database triggers created successfully")
    except Exception as e:
        print(f"Error creating triggers: {e}")
        db.session.rollback()


def create_views():
    """Create database views"""
    
    # View 1: User productivity summary
    view_user_productivity = """
    CREATE VIEW IF NOT EXISTS user_productivity_summary AS
    SELECT 
        u.id as user_id,
        u.name,
        u.email,
        u.department_id,
        d.name as department_name,
        COUNT(DISTINCT ta.task_id) as total_assigned_tasks,
        COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) as completed_tasks,
        ROUND(
            CAST(COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) AS FLOAT) / 
            NULLIF(COUNT(DISTINCT ta.task_id), 0) * 100, 
            2
        ) as completion_percentage,
        COALESCE(SUM(t.actual_hours), 0) as total_hours_worked,
        COUNT(DISTINCT CASE WHEN t.due_date < CURRENT_TIMESTAMP AND t.status != 'done' THEN t.id END) as overdue_tasks
    FROM users u
    LEFT JOIN departments d ON u.department_id = d.id
    LEFT JOIN task_assignees ta ON u.id = ta.user_id
    LEFT JOIN tasks t ON ta.task_id = t.id
    WHERE u.is_active = 1
    GROUP BY u.id, u.name, u.email, u.department_id, d.name;
    """
    
    # View 2: Department efficiency
    view_department_efficiency = """
    CREATE VIEW IF NOT EXISTS department_efficiency AS
    SELECT 
        d.id as department_id,
        d.name as department_name,
        d.organisation_id,
        COUNT(DISTINCT u.id) as total_users,
        COUNT(DISTINCT t.id) as total_tasks,
        COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) as completed_tasks,
        COUNT(DISTINCT CASE WHEN t.status = 'in_progress' THEN t.id END) as in_progress_tasks,
        COUNT(DISTINCT CASE WHEN t.status = 'todo' THEN t.id END) as pending_tasks,
        ROUND(
            CAST(COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) AS FLOAT) / 
            NULLIF(COUNT(DISTINCT t.id), 0) * 100,
            2
        ) as completion_rate,
        COALESCE(AVG(t.actual_hours), 0) as avg_task_hours
    FROM departments d
    LEFT JOIN users u ON d.id = u.department_id AND u.is_active = 1
    LEFT JOIN tasks t ON d.id = t.department_id
    WHERE d.is_active = 1
    GROUP BY d.id, d.name, d.organisation_id;
    """
    
    # View 3: Task overview with assignee info
    view_task_overview = """
    CREATE VIEW IF NOT EXISTS task_overview AS
    SELECT 
        t.id,
        t.title,
        t.status,
        t.priority,
        t.due_date,
        t.created_at,
        t.department_id,
        d.name as department_name,
        creator.name as created_by_name,
        creator.email as created_by_email,
        GROUP_CONCAT(assignee.name, ', ') as assignees,
        COUNT(DISTINCT tc.id) as comment_count,
        COUNT(DISTINCT ta.id) as attachment_count,
        CASE 
            WHEN t.due_date < CURRENT_TIMESTAMP AND t.status != 'done' THEN 1 
            ELSE 0 
        END as is_overdue
    FROM tasks t
    LEFT JOIN departments d ON t.department_id = d.id
    LEFT JOIN users creator ON t.created_by_id = creator.id
    LEFT JOIN task_assignees tas ON t.id = tas.task_id
    LEFT JOIN users assignee ON tas.user_id = assignee.id
    LEFT JOIN task_comments tc ON t.id = tc.task_id
    LEFT JOIN task_attachments ta ON t.id = ta.task_id
    GROUP BY t.id, t.title, t.status, t.priority, t.due_date, t.created_at, 
             t.department_id, d.name, creator.name, creator.email;
    """
    
    # View 4: Recent activity feed
    view_recent_activity = """
    CREATE VIEW IF NOT EXISTS recent_activity AS
    SELECT 
        'task_created' as activity_type,
        t.id as entity_id,
        t.title as activity_title,
        t.created_at as activity_time,
        u.name as user_name,
        t.department_id
    FROM tasks t
    JOIN users u ON t.created_by_id = u.id
    UNION ALL
    SELECT 
        'task_completed' as activity_type,
        t.id as entity_id,
        t.title as activity_title,
        t.completed_date as activity_time,
        u.name as user_name,
        t.department_id
    FROM tasks t
    JOIN users u ON t.created_by_id = u.id
    WHERE t.status = 'done' AND t.completed_date IS NOT NULL
    ORDER BY activity_time DESC
    LIMIT 100;
    """
    
    try:
        db.session.execute(text(view_user_productivity))
        db.session.execute(text(view_department_efficiency))
        db.session.execute(text(view_task_overview))
        db.session.execute(text(view_recent_activity))
        db.session.commit()
        print("✓ Database views created successfully")
    except Exception as e:
        print(f"Error creating views: {e}")
        db.session.rollback()


def create_indexes():
    """Create additional indexes for performance"""
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);",
        "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);",
        "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);",
        "CREATE INDEX IF NOT EXISTS idx_tasks_department ON tasks(department_id);",
        "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);",
        "CREATE INDEX IF NOT EXISTS idx_messages_recipient ON messages(recipient_id);",
        "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_users_organisation ON users(organisation_id);",
        "CREATE INDEX IF NOT EXISTS idx_users_department ON users(department_id);",
    ]
    
    try:
        for index_sql in indexes:
            db.session.execute(text(index_sql))
        db.session.commit()
        print("✓ Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        db.session.rollback()


# SQL Functions (implemented as Python functions due to SQLite limitations)
def calculate_department_completion_percentage(department_id):
    """Calculate completion percentage for a department"""
    result = db.session.execute(
        text("""
            SELECT 
                ROUND(
                    CAST(COUNT(CASE WHEN status = 'done' THEN 1 END) AS FLOAT) / 
                    NULLIF(COUNT(*), 0) * 100,
                    2
                ) as completion_percentage
            FROM tasks
            WHERE department_id = :dept_id
        """),
        {'dept_id': department_id}
    ).fetchone()
    
    return result[0] if result else 0.0


def assign_task_to_least_loaded_user(department_id, task_id):
    """Assign task to user with least number of active tasks in department"""
    result = db.session.execute(
        text("""
            SELECT u.id, COUNT(ta.task_id) as task_count
            FROM users u
            LEFT JOIN task_assignees ta ON u.id = ta.user_id
            LEFT JOIN tasks t ON ta.task_id = t.id AND t.status != 'done'
            WHERE u.department_id = :dept_id AND u.is_active = 1
            GROUP BY u.id
            ORDER BY task_count ASC
            LIMIT 1
        """),
        {'dept_id': department_id}
    ).fetchone()
    
    if result:
        user_id = result[0]
        # Assign the task
        db.session.execute(
            text("INSERT INTO task_assignees (task_id, user_id) VALUES (:task_id, :user_id)"),
            {'task_id': task_id, 'user_id': user_id}
        )
        db.session.commit()
        return user_id
    
    return None


def get_user_productivity_stats(user_id, start_date=None, end_date=None):
    """Get detailed productivity statistics for a user"""
    date_filter = ""
    params = {'user_id': user_id}
    
    if start_date and end_date:
        date_filter = "AND t.created_at BETWEEN :start_date AND :end_date"
        params['start_date'] = start_date
        params['end_date'] = end_date
    
    result = db.session.execute(
        text(f"""
            SELECT 
                COUNT(DISTINCT t.id) as total_tasks,
                COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) as completed_tasks,
                COUNT(DISTINCT CASE WHEN t.status = 'in_progress' THEN t.id END) as in_progress_tasks,
                COALESCE(SUM(t.actual_hours), 0) as total_hours,
                COALESCE(AVG(t.actual_hours), 0) as avg_hours_per_task,
                COUNT(DISTINCT CASE WHEN t.due_date < CURRENT_TIMESTAMP AND t.status != 'done' THEN t.id END) as overdue_tasks
            FROM task_assignees ta
            JOIN tasks t ON ta.task_id = t.id
            WHERE ta.user_id = :user_id {date_filter}
        """),
        params
    ).fetchone()
    
    if result:
        return {
            'total_tasks': result[0],
            'completed_tasks': result[1],
            'in_progress_tasks': result[2],
            'total_hours': result[3],
            'avg_hours_per_task': result[4],
            'overdue_tasks': result[5],
            'completion_rate': (result[1] / result[0] * 100) if result[0] > 0 else 0
        }
    
    return None
