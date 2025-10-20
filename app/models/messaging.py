"""
Messaging and Communication Models
"""

from app import db
from datetime import datetime


class Message(db.Model):
    """Direct and group messages"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # For direct messages
    channel_id = db.Column(db.Integer, db.ForeignKey('chat_channels.id', ondelete='CASCADE'))  # For group messages
    
    # Message type
    message_type = db.Column(db.String(20), default='text')  # text, image, file, task_card
    
    # File/image attachment
    attachment_path = db.Column(db.String(500))
    attachment_filename = db.Column(db.String(255))
    
    # Task card reference (if message_type is task_card)
    task_card_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='SET NULL'))
    
    # Status
    is_delivered = db.Column(db.Boolean, default=False)  # Single tick
    delivered_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)  # Double tick
    read_at = db.Column(db.DateTime)
    is_edited = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], back_populates='received_messages')
    channel = db.relationship('ChatChannel', back_populates='messages')
    task_card = db.relationship('Task')
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            if not self.is_delivered:
                self.is_delivered = True
                self.delivered_at = datetime.utcnow()
    
    def mark_as_delivered(self):
        """Mark message as delivered"""
        if not self.is_delivered:
            self.is_delivered = True
            self.delivered_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Message {self.id}>'


class ChatChannel(db.Model):
    """Group chat channels (department-based or project-based)"""
    __tablename__ = 'chat_channels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    channel_type = db.Column(db.String(20), default='department')  # department, project, custom
    
    # References
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'))
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id', ondelete='CASCADE'), nullable=False)
    
    # Settings
    is_private = db.Column(db.Boolean, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    department = db.relationship('Department')
    organisation = db.relationship('Organisation')
    created_by = db.relationship('User')
    messages = db.relationship('Message', back_populates='channel', cascade='all, delete-orphan', lazy='dynamic', order_by='Message.created_at.desc()')
    members = db.relationship('User', secondary='channel_members', backref='channels')
    
    def __repr__(self):
        return f'<ChatChannel {self.name}>'


# Association table for channel members
channel_members = db.Table('channel_members',
    db.Column('channel_id', db.Integer, db.ForeignKey('chat_channels.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)


class Notification(db.Model):
    """User notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # task_assigned, task_updated, deadline, message, etc.
    
    # Reference to related objects
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'))
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id', ondelete='CASCADE'))
    
    # URL to navigate to
    action_url = db.Column(db.String(500))
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', back_populates='notifications')
    task = db.relationship('Task')
    related_message = db.relationship('Message')
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Notification {self.title}>'


class OnlineStatus(db.Model):
    """Track user online/offline status"""
    __tablename__ = 'online_status'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    socket_id = db.Column(db.String(100))  # Socket.IO session ID
    
    # Relationships
    user = db.relationship('User')
    
    def update_status(self, is_online, socket_id=None):
        """Update user online status"""
        self.is_online = is_online
        self.last_seen = datetime.utcnow()
        if socket_id:
            self.socket_id = socket_id
    
    def __repr__(self):
        return f'<OnlineStatus user_id={self.user_id} online={self.is_online}>'


class TypingIndicator(db.Model):
    """Temporary typing indicators for real-time chat"""
    __tablename__ = 'typing_indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('chat_channels.id', ondelete='CASCADE'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))  # For direct messages
    is_typing = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    channel = db.relationship('ChatChannel')
    recipient = db.relationship('User', foreign_keys=[recipient_id])
    
    def __repr__(self):
        return f'<TypingIndicator user_id={self.user_id}>'
