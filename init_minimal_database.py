"""
Minimal database initialization script for FlowDeck Mini
Creates up to 5 tables: users, tasks, meetings, comments, attachments
"""

from app import db, create_app
from app.models.user import User
from app.models.task import Task
from app.models.meeting import Meeting
from flask import Flask

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Minimal database created with tables: users, tasks, meetings, comments, attachments")
