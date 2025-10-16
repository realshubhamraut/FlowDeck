"""
Notification Socket.IO Events
Real-time notifications
"""

from flask_login import current_user
from flask_socketio import emit
from app import socketio, db
from app.models import Notification


@socketio.on('request_notifications')
def handle_request_notifications():
    """Get unread notifications"""
    if not current_user.is_authenticated:
        return
    
    notifications = current_user.notifications.filter_by(
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    emit('notifications_list', {
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.notification_type,
            'action_url': n.action_url,
            'created_at': n.created_at.isoformat()
        } for n in notifications],
        'unread_count': current_user.notifications.filter_by(is_read=False).count()
    })


def send_notification_to_user(user_id, notification_data):
    """Send notification to specific user via Socket.IO"""
    socketio.emit('new_notification', notification_data, room=f'user_{user_id}')


def broadcast_notification(notification_data, room=None):
    """Broadcast notification to all or specific room"""
    if room:
        socketio.emit('broadcast_notification', notification_data, room=room)
    else:
        socketio.emit('broadcast_notification', notification_data, broadcast=True)
