"""
Database Models for FlowDeck
Normalized relational database design
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import string

# Association tables for many-to-many relationships
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

user_tags = db.Table('user_tags',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

task_tags = db.Table('task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

task_assignees = db.Table('task_assignees',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)


class Organisation(db.Model):
    """Organisation model"""
    __tablename__ = 'organisations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    contact = db.Column(db.String(20))
    logo = db.Column(db.String(255))
    color_palette = db.Column(db.String(50), default='#3498db')
    theme = db.Column(db.String(20), default='light')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    users = db.relationship('User', back_populates='organisation', cascade='all, delete-orphan', lazy='dynamic')
    departments = db.relationship('Department', back_populates='organisation', cascade='all, delete-orphan', lazy='dynamic')
    
    def __repr__(self):
        return f'<Organisation {self.name}>'


class Department(db.Model):
    """Department model"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    organisation = db.relationship('Organisation', back_populates='departments')
    users = db.relationship('User', back_populates='department', lazy='dynamic')
    tasks = db.relationship('Task', back_populates='department', lazy='dynamic')
    
    def __repr__(self):
        return f'<Department {self.name}>'


class Role(db.Model):
    """Role model for RBAC"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text)  # JSON string of permissions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', secondary=user_roles, back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'


class Tag(db.Model):
    """Tag model for categorization"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    color = db.Column(db.String(7), default='#808080')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', secondary=user_tags, back_populates='tags')
    tasks = db.relationship('Task', secondary=task_tags, back_populates='tags')
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class User(UserMixin, db.Model):
    """User model with Flask-Login integration"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    designation = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # Social links
    linkedin = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    github = db.Column(db.String(255))
    
    # Organisation and department
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id', ondelete='CASCADE'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'))
    
    # Status and settings
    is_active = db.Column(db.Boolean, default=True)
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100))
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User preferences
    theme_preference = db.Column(db.String(20), default='light')
    notification_enabled = db.Column(db.Boolean, default=True)
    email_notification_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    organisation = db.relationship('Organisation', back_populates='users')
    department = db.relationship('Department', back_populates='users')
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')
    tags = db.relationship('Tag', secondary=user_tags, back_populates='users')
    
    # Task relationships
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by_id', back_populates='creator', lazy='dynamic')
    assigned_tasks = db.relationship('Task', secondary=task_assignees, back_populates='assignees', lazy='dynamic')
    
    # Comments and notifications
    comments = db.relationship('TaskComment', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    
    # Messages
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', back_populates='recipient', lazy='dynamic')
    
    # Leave requests
    leave_requests = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.user_id', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    approved_leave_requests = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.approved_by_id', back_populates='approved_by', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        """Generate email verification token"""
        self.email_verification_token = secrets.token_urlsafe(32)
        return self.email_verification_token
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.has_role('Admin')
    
    def is_manager(self):
        """Check if user is manager"""
        return self.has_role('Manager') or self.has_role('Admin')
    
    @staticmethod
    def generate_random_password(length=12):
        """Generate a random password"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def is_birthday_today(self):
        """Check if today is user's birthday"""
        if not self.date_of_birth:
            return False
        today = datetime.utcnow().date()
        return (self.date_of_birth.month == today.month and 
                self.date_of_birth.day == today.day)
    
    def age(self):
        """Calculate user's current age"""
        if not self.date_of_birth:
            return None
        today = datetime.utcnow().date()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
        return age
    
    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def username(self):
        """Compatibility alias for templates expecting `username`.

        Some templates reference `user.username`. The canonical field in this
        model is `name`. Expose a `username` property that returns `name`
        (or email as a fallback) to avoid UndefinedError in templates.
        """
        return self.name or self.email
