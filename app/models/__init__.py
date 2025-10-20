"""
Models __init__ - Import all models for easy access
"""

from app.models.user import Organisation, Department, Role, Tag, User
from app.models.task import Task, TaskComment, TaskAttachment, TimeLog, TaskHistory
from app.models.messaging import Message, ChatChannel, Notification, OnlineStatus, TypingIndicator
from app.models.analytics import (
    AnalyticsReport, Holiday, LeaveRequest, AuditLog, 
    SystemSettings, EmailTemplate
)
from app.models.meeting import Meeting, MeetingAgenda, MeetingNote, MeetingAttachment

__all__ = [
    'Organisation', 'Department', 'Role', 'Tag', 'User',
    'Task', 'TaskComment', 'TaskAttachment', 'TimeLog', 'TaskHistory',
    'Message', 'ChatChannel', 'Notification', 'OnlineStatus', 'TypingIndicator',
    'AnalyticsReport', 'Holiday', 'LeaveRequest', 'AuditLog',
    'SystemSettings', 'EmailTemplate',
    'Meeting', 'MeetingAgenda', 'MeetingNote', 'MeetingAttachment'
]
