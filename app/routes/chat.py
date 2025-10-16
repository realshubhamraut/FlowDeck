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
    
    # Get recent direct messages (get the latest message for each conversation)
    from sqlalchemy import func, case
    
    # Get all messages where current user is involved
    all_messages = Message.query.filter(
        db.or_(
            Message.sender_id == current_user.id,
            Message.recipient_id == current_user.id
        ),
        Message.channel_id.is_(None)  # Only direct messages, not channel messages
    ).order_by(Message.created_at.desc()).all()
    
    # Group by conversation partner and keep only the latest message per person
    seen_users = set()
    recent_dms = []
    
    for msg in all_messages:
        # Determine the other user in the conversation
        other_user_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        
        # Only add if we haven't seen this user yet
        if other_user_id not in seen_users:
            seen_users.add(other_user_id)
            recent_dms.append(msg)
            
            # Limit to 10 most recent conversations
            if len(recent_dms) >= 10:
                break
    
    # Get all users in organisation for new message modal
    all_users = User.query.filter_by(
        organisation_id=current_user.organisation_id,
        is_active=True
    ).filter(User.id != current_user.id).order_by(User.name).all()
    
    return render_template('chat/index.html', channels=channels, recent_dms=recent_dms, all_users=all_users)


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
    import os
    from werkzeug.utils import secure_filename
    from flask import current_app
    
    # Check if it's JSON or FormData
    if request.is_json:
        data = request.get_json()
        content = data.get('content', '').strip()
        recipient_id = data.get('recipient_id')
        channel_id = data.get('channel_id')
        message_type = data.get('message_type', 'text')
        task_card_id = data.get('task_card_id')
        attachment_path = None
        attachment_filename = None
    else:
        # FormData (for image uploads)
        content = request.form.get('content', '').strip()
        recipient_id = request.form.get('recipient_id')
        channel_id = request.form.get('channel_id')
        message_type = request.form.get('message_type', 'text')
        task_card_id = request.form.get('task_card_id')
        attachment_path = None
        attachment_filename = None
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                # Secure filename
                original_filename = secure_filename(image_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{current_user.id}_{timestamp}_{original_filename}"
                
                # Create upload directory if not exists
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'chat')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                file_path = os.path.join(upload_dir, filename)
                image_file.save(file_path)
                
                # Set attachment path
                attachment_path = f'/static/uploads/chat/{filename}'
                attachment_filename = original_filename
                message_type = 'image'
    
    if not content and not attachment_path:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Convert recipient_id and channel_id to int if present
    if recipient_id:
        recipient_id = int(recipient_id)
    if channel_id:
        channel_id = int(channel_id)
    if task_card_id:
        task_card_id = int(task_card_id)
    
    # Create message
    message = Message(
        content=content or 'Sent an image',
        sender_id=current_user.id,
        recipient_id=recipient_id,
        channel_id=channel_id,
        message_type=message_type,
        task_card_id=task_card_id,
        attachment_path=attachment_path,
        attachment_filename=attachment_filename
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Emit Socket.IO event (handled by socket events)
    from app import socketio
    socket_data = {
        'id': message.id,
        'content': message.content,
        'sender': current_user.name,
        'sender_id': current_user.id,
        'created_at': message.created_at.isoformat(),
        'message_type': message_type,
        'attachment_url': attachment_path
    }
    
    if channel_id:
        socketio.emit('new_message', socket_data, room=f'channel_{channel_id}')
    elif recipient_id:
        socketio.emit('new_direct_message', socket_data, room=f'user_{recipient_id}')
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'content': message.content,
            'sender': current_user.name,
            'created_at': message.created_at.isoformat(),
            'message_type': message_type,
            'attachment_url': attachment_path
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
