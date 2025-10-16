"""
Chat Blueprint - Messaging and communication
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Message, ChatChannel, User, Task
from datetime import datetime

bp = Blueprint('chat', __name__, url_prefix='/chat')


@bp.route('/')
@login_required
def index():
    """Chat interface"""
    # Get user's channels
    channels = current_user.channels
    
    # Get recent direct messages
    recent_dms = db.session.query(User).join(
        Message, db.or_(
            Message.sender_id == User.id,
            Message.recipient_id == User.id
        )
    ).filter(
        db.or_(
            Message.sender_id == current_user.id,
            Message.recipient_id == current_user.id
        )
    ).distinct().limit(10).all()
    
    return render_template('chat/index.html', channels=channels, recent_dms=recent_dms)


@bp.route('/channel/<int:channel_id>')
@login_required
def channel(channel_id):
    """View channel messages"""
    channel = ChatChannel.query.get_or_404(channel_id)
    
    # Check if user is member
    if current_user not in channel.members:
        flash('You are not a member of this channel.', 'danger')
        return redirect(url_for('chat.index'))
    
    # Get messages
    messages = channel.messages.order_by(Message.created_at.asc()).limit(100).all()
    
    # Mark messages as read
    for msg in messages:
        if msg.recipient_id == current_user.id and not msg.is_read:
            msg.mark_as_read()
    
    db.session.commit()
    
    return render_template('chat/channel.html', channel=channel, messages=messages)


@bp.route('/direct/<int:user_id>')
@login_required
def direct(user_id):
    """Direct message with user"""
    user = User.query.get_or_404(user_id)
    
    # Check same organisation
    if user.organisation_id != current_user.organisation_id:
        flash('User not found.', 'danger')
        return redirect(url_for('chat.index'))
    
    # Get messages between users
    messages = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.recipient_id == user_id),
            db.and_(Message.sender_id == user_id, Message.recipient_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).limit(100).all()
    
    # Mark messages as read
    for msg in messages:
        if msg.recipient_id == current_user.id and not msg.is_read:
            msg.mark_as_read()
    
    db.session.commit()
    
    return render_template('chat/direct.html', recipient=user, messages=messages)


@bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send a message (AJAX)"""
    data = request.get_json()
    
    content = data.get('content', '').strip()
    recipient_id = data.get('recipient_id')
    channel_id = data.get('channel_id')
    message_type = data.get('message_type', 'text')
    task_card_id = data.get('task_card_id')
    
    if not content:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Create message
    message = Message(
        content=content,
        sender_id=current_user.id,
        recipient_id=recipient_id,
        channel_id=channel_id,
        message_type=message_type,
        task_card_id=task_card_id
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Emit Socket.IO event (handled by socket events)
    from app import socketio
    if channel_id:
        socketio.emit('new_message', {
            'id': message.id,
            'content': message.content,
            'sender': current_user.name,
            'sender_id': current_user.id,
            'created_at': message.created_at.isoformat(),
            'message_type': message_type
        }, room=f'channel_{channel_id}')
    elif recipient_id:
        socketio.emit('new_direct_message', {
            'id': message.id,
            'content': message.content,
            'sender': current_user.name,
            'sender_id': current_user.id,
            'created_at': message.created_at.isoformat(),
            'message_type': message_type
        }, room=f'user_{recipient_id}')
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'content': message.content,
            'sender': current_user.name,
            'created_at': message.created_at.isoformat()
        }
    })


@bp.route('/channels/create', methods=['GET', 'POST'])
@login_required
def create_channel():
    """Create new chat channel"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_private = request.form.get('is_private') == 'on'
        member_ids = request.form.getlist('members')
        
        if not name:
            flash('Channel name is required.', 'warning')
            return render_template('chat/create_channel.html', 
                                 users=get_organisation_users())
        
        channel = ChatChannel(
            name=name,
            description=description,
            channel_type='custom',
            is_private=is_private,
            organisation_id=current_user.organisation_id,
            created_by_id=current_user.id
        )
        
        db.session.add(channel)
        db.session.flush()
        
        # Add members
        if member_ids:
            members = User.query.filter(User.id.in_(member_ids)).all()
            channel.members.extend(members)
        
        # Add creator as member
        if current_user not in channel.members:
            channel.members.append(current_user)
        
        db.session.commit()
        
        flash(f'Channel "{name}" created successfully!', 'success')
        return redirect(url_for('chat.channel', channel_id=channel.id))
    
    return render_template('chat/create_channel.html', users=get_organisation_users())


@bp.route('/search')
@login_required
def search():
    """Search messages"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('chat/search.html', messages=[])
    
    # Search in messages where user is involved
    messages = Message.query.filter(
        db.and_(
            Message.content.ilike(f'%{query}%'),
            db.or_(
                Message.sender_id == current_user.id,
                Message.recipient_id == current_user.id,
                Message.channel_id.in_(
                    db.session.query(ChatChannel.id).join(
                        ChatChannel.members
                    ).filter(User.id == current_user.id)
                )
            )
        )
    ).order_by(Message.created_at.desc()).limit(50).all()
    
    return render_template('chat/search.html', messages=messages, query=query)


def get_organisation_users():
    """Get all users in organisation"""
    return User.query.filter_by(
        organisation_id=current_user.organisation_id,
        is_active=True
    ).filter(User.id != current_user.id).order_by(User.name).all()
