"""
Task and Project Management Models
"""

from app import db
from datetime import datetime
import json


class Task(db.Model):
    """Task model with Kanban board support"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Status and priority
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, done, archived
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Dates
    due_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Time tracking
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float, default=0.0)
    
    # Relationships
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'))
    
    # Kanban board position
    board_column = db.Column(db.String(20), default='todo')
    board_position = db.Column(db.Integer, default=0)
    
    # AI generated
    is_ai_generated = db.Column(db.Boolean, default=False)
    ai_metadata = db.Column(db.Text)  # JSON metadata from AI
    
    # Deliverables (stored as JSON)
    deliverables = db.Column(db.Text)  # JSON array of deliverable items
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by_id], back_populates='created_tasks')
    assignees = db.relationship('User', secondary='task_assignees', back_populates='assigned_tasks')
    department = db.relationship('Department', back_populates='tasks')
    tags = db.relationship('Tag', secondary='task_tags', back_populates='tasks')
    
    comments = db.relationship('TaskComment', back_populates='task', cascade='all, delete-orphan', lazy='dynamic', order_by='TaskComment.created_at.desc()')
    attachments = db.relationship('TaskAttachment', back_populates='task', cascade='all, delete-orphan', lazy='dynamic')
    time_logs = db.relationship('TimeLog', back_populates='task', cascade='all, delete-orphan', lazy='dynamic')
    
    def get_deliverables(self):
        """Parse and return deliverables list"""
        if self.deliverables:
            try:
                return json.loads(self.deliverables)
            except:
                return []
        return []
    
    def set_deliverables(self, items):
        """Set deliverables from list"""
        self.deliverables = json.dumps(items)
    
    def get_completion_percentage(self):
        """Calculate task completion percentage based on deliverables"""
        deliverables = self.get_deliverables()
        if not deliverables:
            return 100 if self.status == 'done' else 0
        
        completed = sum(1 for item in deliverables if item.get('completed', False))
        return int((completed / len(deliverables)) * 100)
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != 'done':
            return datetime.utcnow() > self.due_date
        return False
    
    def get_time_spent(self):
        """Get total time spent on task from time logs"""
        total = sum(log.duration for log in self.time_logs if log.duration)
        return total
    
    def __repr__(self):
        return f'<Task {self.title}>'


class TaskComment(db.Model):
    """Comments on tasks"""
    __tablename__ = 'task_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('task_comments.id', ondelete='CASCADE'))  # For threaded comments
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_edited = db.Column(db.Boolean, default=False)
    
    # Relationships
    task = db.relationship('Task', back_populates='comments')
    user = db.relationship('User', back_populates='comments')
    replies = db.relationship('TaskComment', backref=db.backref('parent', remote_side=[id]), cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TaskComment {self.id}>'


class TaskAttachment(db.Model):
    """File attachments for tasks"""
    __tablename__ = 'task_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    mime_type = db.Column(db.String(100))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    task = db.relationship('Task', back_populates='attachments')
    uploaded_by = db.relationship('User')
    
    def get_file_size_formatted(self):
        """Return formatted file size"""
        if not self.file_size:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"
    
    def __repr__(self):
        return f'<TaskAttachment {self.filename}>'


class TimeLog(db.Model):
    """Time tracking for tasks"""
    __tablename__ = 'time_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Float)  # Duration in hours
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    task = db.relationship('Task', back_populates='time_logs')
    user = db.relationship('User')
    
    def calculate_duration(self):
        """Calculate duration from start and end time"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration = delta.total_seconds() / 3600  # Convert to hours
        return self.duration
    
    def __repr__(self):
        return f'<TimeLog {self.id}>'


class TaskHistory(db.Model):
    """Audit log for task changes"""
    __tablename__ = 'task_history'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    action = db.Column(db.String(50), nullable=False)  # created, updated, status_changed, assigned, etc.
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    field_changed = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    task = db.relationship('Task')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<TaskHistory {self.action}>'
