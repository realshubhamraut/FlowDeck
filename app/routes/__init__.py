"""
Routes __init__ - Import all blueprints
"""

from app.routes import auth, main, admin, user, tasks, chat, dashboard, api, meetings

__all__ = ['auth', 'main', 'admin', 'user', 'tasks', 'chat', 'dashboard', 'api', 'meetings']
