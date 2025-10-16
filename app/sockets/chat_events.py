"""
Chat Socket.IO Events
Real-time messaging functionality
"""

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models import Message, OnlineStatus, TypingIndicator, ChatChannel


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        # Update online status
        online_status = OnlineStatus.query.filter_by(user_id=current_user.id).first()
        if not online_status:
            online_status = OnlineStatus(user_id=current_user.id)
            db.session.add(online_status)
        
        online_status.update_status(True, request.sid)
        db.session.commit()
        
        # Join user's personal room
        join_room(f'user_{current_user.id}')
        
        # Join all channel rooms
        for channel in current_user.channels:
            join_room(f'channel_{channel.id}')
        
        # Broadcast user online status
        emit('user_online', {
            'user_id': current_user.id,
            'user_name': current_user.name
        }, broadcast=True)
        
        print(f'User {current_user.name} connected')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        # Update online status
        online_status = OnlineStatus.query.filter_by(user_id=current_user.id).first()
        if online_status:
            online_status.update_status(False)
            db.session.commit()
        
        # Broadcast user offline status
        emit('user_offline', {
            'user_id': current_user.id,
            'user_name': current_user.name
        }, broadcast=True)
        
        print(f'User {current_user.name} disconnected')


@socketio.on('join_channel')
def handle_join_channel(data):
    """Join a channel room"""
    if not current_user.is_authenticated:
        return
    
    channel_id = data.get('channel_id')
    if not channel_id:
        return
    
    # Verify user is member of channel
    channel = ChatChannel.query.get(channel_id)
    if channel and current_user in channel.members:
        join_room(f'channel_{channel_id}')
        emit('joined_channel', {
            'channel_id': channel_id,
            'user_name': current_user.name
        }, room=f'channel_{channel_id}')


@socketio.on('leave_channel')
def handle_leave_channel(data):
    """Leave a channel room"""
    if not current_user.is_authenticated:
        return
    
    channel_id = data.get('channel_id')
    if not channel_id:
        return
    
    leave_room(f'channel_{channel_id}')
    emit('left_channel', {
        'channel_id': channel_id,
        'user_name': current_user.name
    }, room=f'channel_{channel_id}')


@socketio.on('send_message')
def handle_send_message(data):
    """Handle sending a message"""
    if not current_user.is_authenticated:
        return
    
    content = data.get('content', '').strip()
    recipient_id = data.get('recipient_id')
    channel_id = data.get('channel_id')
    message_type = data.get('message_type', 'text')
    
    if not content:
        return
    
    # Create message
    message = Message(
        content=content,
        sender_id=current_user.id,
        recipient_id=recipient_id,
        channel_id=channel_id,
        message_type=message_type
    )
    
    db.session.add(message)
    db.session.commit()
    
    message_data = {
        'id': message.id,
        'content': message.content,
        'sender_id': current_user.id,
        'sender_name': current_user.name,
        'sender_picture': current_user.profile_picture,
        'created_at': message.created_at.isoformat(),
        'message_type': message_type
    }
    
    # Emit to appropriate room
    if channel_id:
        emit('new_message', message_data, room=f'channel_{channel_id}')
    elif recipient_id:
        # Send to recipient and sender
        emit('new_direct_message', message_data, room=f'user_{recipient_id}')
        emit('new_direct_message', message_data, room=f'user_{current_user.id}')


@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator"""
    if not current_user.is_authenticated:
        return
    
    recipient_id = data.get('recipient_id')
    channel_id = data.get('channel_id')
    is_typing = data.get('is_typing', True)
    
    typing_data = {
        'user_id': current_user.id,
        'user_name': current_user.name,
        'is_typing': is_typing
    }
    
    if channel_id:
        emit('user_typing', typing_data, room=f'channel_{channel_id}', include_self=False)
    elif recipient_id:
        emit('user_typing', typing_data, room=f'user_{recipient_id}')


@socketio.on('request_online_users')
def handle_request_online_users():
    """Get list of online users"""
    if not current_user.is_authenticated:
        return
    
    online_users = OnlineStatus.query.filter_by(is_online=True).all()
    
    emit('online_users_list', {
        'users': [{
            'user_id': status.user_id,
            'user_name': status.user.name if status.user else 'Unknown',
            'last_seen': status.last_seen.isoformat()
        } for status in online_users]
    })


@socketio.on('mark_message_read')
def handle_mark_message_read(data):
    """Mark message as read"""
    if not current_user.is_authenticated:
        return
    
    message_id = data.get('message_id')
    if not message_id:
        return
    
    message = Message.query.get(message_id)
    if message and message.recipient_id == current_user.id:
        message.mark_as_read()
        db.session.commit()
        
        # Notify sender that message was read
        emit('message_read', {
            'message_id': message_id,
            'read_by': current_user.id
        }, room=f'user_{message.sender_id}')
