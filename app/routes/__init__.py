"""
Routes __init__ - Import all blueprints
"""

from app.routes import admin, user, tasks, meetings, dashboard

__all__ = ['admin', 'user', 'tasks', 'meetings', 'dashboard']
