"""
Analytics, Reports, Holidays, and Leave Management Models
"""

from app import db
from datetime import datetime
import json


class AnalyticsReport(db.Model):
    """Store analytics and reports"""
    __tablename__ = 'analytics_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id', ondelete='CASCADE'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # weekly, monthly, department, user
    report_period_start = db.Column(db.DateTime, nullable=False)
    report_period_end = db.Column(db.DateTime, nullable=False)
    
    # Metrics stored as JSON
    metrics = db.Column(db.Text, nullable=False)  # JSON data with all metrics
    
    # Summary fields (denormalized for quick access)
    tasks_created = db.Column(db.Integer, default=0)
    tasks_completed = db.Column(db.Integer, default=0)
    completion_rate = db.Column(db.Float, default=0.0)
    average_task_time = db.Column(db.Float, default=0.0)  # In hours
    
    # Department/User specific (optional)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    
    # Status
    is_generated = db.Column(db.Boolean, default=False)
    generated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organisation = db.relationship('Organisation')
    department = db.relationship('Department')
    user = db.relationship('User')
    
    def get_metrics(self):
        """Parse and return metrics"""
        if self.metrics:
            try:
                return json.loads(self.metrics)
            except:
                return {}
        return {}
    
    def set_metrics(self, data):
        """Set metrics from dictionary"""
        self.metrics = json.dumps(data)
    
    def __repr__(self):
        return f'<AnalyticsReport {self.report_type} {self.report_period_start}>'


class Holiday(db.Model):
    """Store holidays and events"""
    __tablename__ = 'holidays'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, index=True)
    holiday_type = db.Column(db.String(50), default='public')  # public, optional, organisation
    country = db.Column(db.String(50), default='IN')
    
    # Organisation specific (null for public holidays)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id', ondelete='CASCADE'))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organisation = db.relationship('Organisation')
    
    def __repr__(self):
        return f'<Holiday {self.name} on {self.date}>'


class LeaveRequest(db.Model):
    """Employee leave requests"""
    __tablename__ = 'leave_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # sick, casual, vacation, emergency
    
    # Date range
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, nullable=False)
    
    # Reason and details
    reason = db.Column(db.Text, nullable=False)
    supporting_document = db.Column(db.String(500))  # Path to uploaded document
    
    # Approval workflow
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    approval_notes = db.Column(db.Text)
    approved_at = db.Column(db.DateTime)
    
    # Timestamps
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], back_populates='leave_requests')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], back_populates='approved_leave_requests')
    
    def calculate_days(self):
        """Calculate total days between start and end date"""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.total_days = delta.days + 1
        return self.total_days
    
    def __repr__(self):
        return f'<LeaveRequest {self.user_id} {self.leave_type}>'


class AuditLog(db.Model):
    """System audit log for tracking all actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id', ondelete='CASCADE'))
    
    # Action details
    action = db.Column(db.String(100), nullable=False)  # user_created, task_assigned, etc.
    entity_type = db.Column(db.String(50))  # User, Task, Organisation, etc.
    entity_id = db.Column(db.Integer)
    
    # Changes
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    
    # Context
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User')
    organisation = db.relationship('Organisation')
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'


class SystemSettings(db.Model):
    """System-wide and organisation-specific settings"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id', ondelete='CASCADE'))
    
    # Setting key-value
    setting_key = db.Column(db.String(100), nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20), default='string')  # string, int, bool, json
    
    # Metadata
    description = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=False)  # Can users see this setting
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organisation = db.relationship('Organisation')
    
    def get_value(self):
        """Get parsed value based on type"""
        if self.setting_type == 'int':
            return int(self.setting_value)
        elif self.setting_type == 'bool':
            return self.setting_value.lower() == 'true'
        elif self.setting_type == 'json':
            try:
                return json.loads(self.setting_value)
            except:
                return {}
        return self.setting_value
    
    def __repr__(self):
        return f'<SystemSettings {self.setting_key}>'


class EmailTemplate(db.Model):
    """Email templates for notifications"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    subject = db.Column(db.String(255), nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    body_text = db.Column(db.Text)
    
    # Template variables (stored as JSON)
    variables = db.Column(db.Text)  # List of available variables
    
    # Metadata
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_variables(self):
        """Get list of template variables"""
        if self.variables:
            try:
                return json.loads(self.variables)
            except:
                return []
        return []
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'
