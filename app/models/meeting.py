"""
Meeting Management Models
"""

from app import db
from datetime import datetime


# Association table for meeting attendees
meeting_attendees = db.Table('meeting_attendees',
    db.Column('meeting_id', db.Integer, db.ForeignKey('meetings.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('status', db.String(20), default='pending'),  # pending, accepted, declined, tentative
    db.Column('responded_at', db.DateTime)
)


class Meeting(db.Model):
    """Meeting model for scheduling and managing meetings"""
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Meeting type
    meeting_type = db.Column(db.String(50), default='general')  # general, standup, review, planning, client, one-on-one
    
    # Location
    location = db.Column(db.String(200))  # Physical location or meeting room
    meeting_link = db.Column(db.String(500))  # Video conference link (Zoom, Teams, Meet, etc.)
    
    # Timing
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    
    # Recurrence
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(50))  # daily, weekly, monthly, yearly
    recurrence_end_date = db.Column(db.DateTime)
    
    # Reminders
    reminder_minutes = db.Column(db.Integer, default=15)  # Remind X minutes before
    send_email_reminder = db.Column(db.Boolean, default=True)
    
    # Priority and visibility
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    is_private = db.Column(db.Boolean, default=False)
    
    # Related entities
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='SET NULL'))  # Optional: link to task
    
    # Organizer
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organizer = db.relationship('User', foreign_keys=[organizer_id], backref='organized_meetings')
    attendees = db.relationship('User', secondary=meeting_attendees, backref='attending_meetings')
    department = db.relationship('Department', backref='meetings')
    task = db.relationship('Task', backref='meetings')
    
    agenda_items = db.relationship('MeetingAgendaItem', back_populates='meeting', cascade='all, delete-orphan', order_by='MeetingAgendaItem.order')
    notes = db.relationship('MeetingNote', back_populates='meeting', cascade='all, delete-orphan', order_by='MeetingNote.created_at.desc()')
    attachments = db.relationship('MeetingAttachment', back_populates='meeting', cascade='all, delete-orphan')
    
    def get_duration_minutes(self):
        """Calculate meeting duration in minutes"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return 0
    
    def is_upcoming(self):
        """Check if meeting is upcoming"""
        return self.start_time > datetime.utcnow() and self.status == 'scheduled'
    
    def is_ongoing(self):
        """Check if meeting is currently in progress"""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time and self.status in ['scheduled', 'in_progress']
    
    def is_past(self):
        """Check if meeting has ended"""
        return self.end_time < datetime.utcnow() or self.status in ['completed', 'cancelled']
    
    def get_attendee_status(self, user_id):
        """Get attendance status for a specific user"""
        result = db.session.execute(
            db.select(meeting_attendees.c.status).where(
                db.and_(
                    meeting_attendees.c.meeting_id == self.id,
                    meeting_attendees.c.user_id == user_id
                )
            )
        ).first()
        return result[0] if result else None
    
    def get_response_stats(self):
        """Get meeting response statistics"""
        results = db.session.execute(
            db.select(
                meeting_attendees.c.status,
                db.func.count(meeting_attendees.c.user_id)
            ).where(
                meeting_attendees.c.meeting_id == self.id
            ).group_by(meeting_attendees.c.status)
        ).all()
        
        stats = {'accepted': 0, 'declined': 0, 'tentative': 0, 'pending': 0}
        for status, count in results:
            stats[status] = count
        return stats
    
    def __repr__(self):
        return f'<Meeting {self.title}>'


class MeetingAgendaItem(db.Model):
    """Agenda items for meetings"""
    __tablename__ = 'meeting_agenda'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer)  # Estimated duration for this agenda item
    order = db.Column(db.Integer, default=0)  # Order of agenda items
    is_completed = db.Column(db.Boolean, default=False)
    
    # Relationships
    meeting = db.relationship('Meeting', back_populates='agenda_items')
    
    def __repr__(self):
        return f'<MeetingAgendaItem {self.title}>'


class MeetingNote(db.Model):
    """Notes taken during or after meetings"""
    __tablename__ = 'meeting_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    note_type = db.Column(db.String(50), default='general')  # general, action_item, decision, follow_up
    
    # Author
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    meeting = db.relationship('Meeting', back_populates='notes')
    created_by = db.relationship('User')
    
    def __repr__(self):
        return f'<MeetingNote {self.id}>'


class MeetingAttachment(db.Model):
    """File attachments for meetings"""
    __tablename__ = 'meeting_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    meeting = db.relationship('Meeting', back_populates='attachments')
    uploaded_by = db.relationship('User')
    
    def get_file_size_formatted(self):
        """Return formatted file size"""
        if not self.file_size:
            return "Unknown"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def __repr__(self):
        return f'<MeetingAttachment {self.filename}>'
