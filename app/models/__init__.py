"""
Models __init__ - Import all models for easy access
"""

from app.models.user import User
from app.models.task import Task
from app.models.meeting import Meeting

__all__ = [
    'User',
    'Task',
    'Meeting'
]
