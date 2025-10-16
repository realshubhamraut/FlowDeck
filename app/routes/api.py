"""
API Blueprint - REST API endpoints
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Task, User, Department, Notification, Message
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api/v1')


@bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get tasks (API)"""
    status = request.args.get('status')
    priority = request.args.get('priority')
    limit = request.args.get('limit', 50, type=int)
    
    query = current_user.assigned_tasks
    
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    
    tasks = query.order_by(Task.due_date.asc()).limit(limit).all()
    
    return jsonify({
        'tasks': [{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'created_at': task.created_at.isoformat(),
            'is_overdue': task.is_overdue()
        } for task in tasks]
    })


@bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Get single task (API)"""
    task = Task.query.get_or_404(task_id)
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'created_at': task.created_at.isoformat(),
        'assignees': [{'id': u.id, 'name': u.name} for u in task.assignees],
        'deliverables': task.get_deliverables(),
        'completion_percentage': task.get_completion_percentage()
    })


@bp.route('/tasks/<int:task_id>', methods=['PATCH'])
@login_required
def update_task_api(task_id):
    """Update task (API)"""
    task = Task.query.get_or_404(task_id)
    
    data = request.get_json()
    
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    
    db.session.commit()
    
    return jsonify({'success': True, 'task_id': task.id})


@bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get notifications (API)"""
    unread_only = request.args.get('unread', 'false').lower() == 'true'
    limit = request.args.get('limit', 20, type=int)
    
    query = current_user.notifications
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.notification_type,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
            'action_url': n.action_url
        } for n in notifications],
        'unread_count': current_user.notifications.filter_by(is_read=False).count()
    })


@bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_notification_read_api(notif_id):
    """Mark notification as read (API)"""
    notif = Notification.query.get_or_404(notif_id)
    
    if notif.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notif.mark_as_read()
    db.session.commit()
    
    return jsonify({'success': True})


@bp.route('/messages/unread-count', methods=['GET'])
@login_required
def unread_messages_count():
    """Get unread messages count (API)"""
    count = Message.query.filter_by(
        recipient_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({'unread_count': count})


@bp.route('/users/search', methods=['GET'])
@login_required
def search_users():
    """Search users (API)"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'users': []})
    
    users = User.query.filter(
        User.organisation_id == current_user.organisation_id,
        User.is_active == True,
        db.or_(
            User.name.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify({
        'users': [{
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'designation': u.designation,
            'profile_picture': u.profile_picture
        } for u in users]
    })


@bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get user stats (API)"""
    stats = {
        'total_tasks': current_user.assigned_tasks.count(),
        'completed_tasks': current_user.assigned_tasks.filter_by(status='done').count(),
        'in_progress_tasks': current_user.assigned_tasks.filter_by(status='in_progress').count(),
        'todo_tasks': current_user.assigned_tasks.filter_by(status='todo').count(),
        'overdue_tasks': current_user.assigned_tasks.filter(
            db.and_(Task.due_date < datetime.utcnow(), Task.status != 'done')
        ).count(),
        'unread_notifications': current_user.notifications.filter_by(is_read=False).count(),
        'unread_messages': Message.query.filter_by(
            recipient_id=current_user.id, is_read=False
        ).count()
    }
    
    if stats['total_tasks'] > 0:
        stats['completion_rate'] = round(
            (stats['completed_tasks'] / stats['total_tasks']) * 100, 2
        )
    else:
        stats['completion_rate'] = 0
    
    return jsonify(stats)


@bp.route('/ai/generate-task', methods=['POST'])
@login_required
def generate_ai_task():
    """Generate AI task card"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        from app.utils.ai import generate_task_from_prompt
        task_data = generate_task_from_prompt(prompt)
        
        return jsonify({
            'success': True,
            'task': task_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
