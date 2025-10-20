"""
Dashboard Blueprint - User dashboard
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Task, Notification, Message, Department, User
from app.utils.quotes import get_daily_quote, get_birthday_message
from sqlalchemy import text, or_, and_, extract
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
@login_required
def index():
    """Main dashboard"""
    # Get user's assigned tasks
    tasks = current_user.assigned_tasks.filter(
        Task.status.in_(['todo', 'in_progress'])
    ).order_by(Task.due_date.asc()).limit(10).all()
    
    # Get all tasks for Kanban board (grouped by status)
    all_tasks = current_user.assigned_tasks.order_by(Task.due_date.asc()).all()
    tasks_by_status = {
        'todo': [t for t in all_tasks if t.status == 'todo'],
        'in_progress': [t for t in all_tasks if t.status == 'in_progress'],
        'done': [t for t in all_tasks if t.status == 'done']
    }
    
    # Get unread notifications
    notifications = current_user.notifications.filter_by(
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Get recent messages
    recent_messages = Message.query.filter(
        or_(
            Message.recipient_id == current_user.id,
            Message.sender_id == current_user.id
        )
    ).order_by(Message.created_at.desc()).limit(5).all()
    
    # Get statistics
    stats = {
        'total_tasks': current_user.assigned_tasks.count(),
        'completed_tasks': current_user.assigned_tasks.filter_by(status='done').count(),
        'in_progress_tasks': current_user.assigned_tasks.filter_by(status='in_progress').count(),
        'overdue_tasks': current_user.assigned_tasks.filter(
            and_(Task.due_date < datetime.utcnow(), Task.status != 'done')
        ).count(),
        'unread_notifications': current_user.notifications.filter_by(is_read=False).count(),
        'unread_messages': Message.query.filter_by(
            recipient_id=current_user.id, is_read=False
        ).count()
    }
    
    # Get upcoming tasks (next 7 days)
    next_week = datetime.utcnow() + timedelta(days=7)
    upcoming_tasks = current_user.assigned_tasks.filter(
        and_(
            Task.due_date >= datetime.utcnow(),
            Task.due_date <= next_week,
            Task.status != 'done'
        )
    ).order_by(Task.due_date.asc()).all()
    
    # Get today's birthdays from the organization
    today = datetime.utcnow().date()
    birthday_users = User.query.filter(
        User.organisation_id == current_user.organisation_id,
        User.is_active == True,
        extract('month', User.date_of_birth) == today.month,
        extract('day', User.date_of_birth) == today.day
    ).all()
    
    # Prepare birthday messages
    birthday_wishes = []
    for user in birthday_users:
        age = user.age() if user.date_of_birth else None
        birthday_wishes.append({
            'user': user,
            'message': get_birthday_message(user.name, age),
            'age': age
        })
    
    # Get daily motivational quote
    daily_quote = get_daily_quote()
    
    return render_template('dashboard/index.html',
                         tasks=tasks,
                         tasks_by_status=tasks_by_status,
                         notifications=notifications,
                         messages=recent_messages,
                         upcoming_tasks=upcoming_tasks,
                         recent_notifications=notifications,
                         total_tasks=stats['total_tasks'],
                         completed_tasks=stats['completed_tasks'],
                         in_progress_tasks=stats['in_progress_tasks'],
                         overdue_tasks=stats['overdue_tasks'],
                         unread_notifications=stats['unread_notifications'],
                         unread_messages=stats['unread_messages'],
                         birthday_wishes=birthday_wishes,
                         daily_quote=daily_quote)


@bp.route('/analytics')
@login_required
def analytics():
    """User analytics"""
    from app.database import get_user_productivity_stats
    
    # Get user's productivity stats
    stats = get_user_productivity_stats(current_user.id)
    
    # Get weekly stats for chart
    weekly_stats = db.session.execute(text("""
        SELECT 
            DATE(created_at) as date,
            COUNT(CASE WHEN status = 'done' THEN 1 END) as completed,
            COUNT(*) as total
        FROM tasks t
        JOIN task_assignees ta ON t.id = ta.task_id
        WHERE ta.user_id = :user_id 
        AND t.created_at >= DATE('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    """), {'user_id': current_user.id}).fetchall()
    
    # Get task breakdown by status
    status_breakdown = db.session.execute(text("""
        SELECT 
            t.status,
            COUNT(*) as count
        FROM tasks t
        JOIN task_assignees ta ON t.id = ta.task_id
        WHERE ta.user_id = :user_id
        GROUP BY t.status
    """), {'user_id': current_user.id}).fetchall()
    
    # Get task breakdown by priority
    priority_breakdown = db.session.execute(text("""
        SELECT 
            t.priority,
            COUNT(*) as count
        FROM tasks t
        JOIN task_assignees ta ON t.id = ta.task_id
        WHERE ta.user_id = :user_id
        GROUP BY t.priority
    """), {'user_id': current_user.id}).fetchall()
    
    return render_template('dashboard/analytics.html',
                         stats=stats,
                         weekly_stats=weekly_stats,
                         status_breakdown=status_breakdown,
                         priority_breakdown=priority_breakdown)


@bp.route('/calendar')
@login_required
def calendar():
    """Calendar view of tasks"""
    return render_template('dashboard/calendar.html')


@bp.route('/calendar/events')
@login_required
def calendar_events():
    """Get calendar events (AJAX endpoint)"""
    import requests
    from flask import current_app
    
    start_param = request.args.get('start')
    end_param = request.args.get('end')

    # Parse incoming date params; default to +-30 days window
    now = datetime.utcnow()
    default_start = now - timedelta(days=30)
    default_end = now + timedelta(days=30)
    
    def _parse_dt(value, fallback):
        if not value:
            return fallback
        try:
            # FullCalendar typically sends ISO 8601
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except Exception:
            return fallback

    start = _parse_dt(start_param, default_start)
    end = _parse_dt(end_param, default_end)

    # Get tasks that have either start_date or due_date within the range
    tasks = current_user.assigned_tasks.filter(
        or_(
            and_(
                Task.start_date.isnot(None),
                Task.start_date <= end,
                or_(Task.due_date.isnot(None), Task.start_date >= start)
            ),
            and_(
                Task.due_date.isnot(None),
                Task.due_date >= start,
                Task.due_date <= end
            )
        )
    ).all()
    
    # Build tasks list for response
    events = []
    for task in tasks:
        # Use due_date for display (more important than start_date for tasks)
        task_date = task.due_date if task.due_date else task.start_date
        if task_date:
            events.append({
                'id': task.id,
                'title': task.title,
                'start': task.start_date.isoformat() if task.start_date else task_date.isoformat(),
                'end': task_date.isoformat(),
                'due_date': task_date.isoformat(),
                'priority': task.priority,
                'status': task.status,
                'url': f'/tasks/view/{task.id}',
                'backgroundColor': {
                    'urgent': '#dc3545',
                    'high': '#fd7e14',
                    'medium': '#ffc107',
                    'low': '#28a745'
                }.get(task.priority, '#6c757d'),
                'borderColor': {
                    'urgent': '#dc3545',
                    'high': '#fd7e14',
                    'medium': '#ffc107',
                    'low': '#28a745'
                }.get(task.priority, '#6c757d'),
                'classNames': ['task-event'],
                'extendedProps': {
                    'type': 'task'
                }
            })
    
    # Fetch holidays from Calendarific API (free tier)
    try:
        # Get API key from environment or config
        api_key = current_app.config.get('CALENDARIFIC_API_KEY', '6TJzcgLLBWlS4TsrNJ6u0HMiVaF8QPRM')
        year = start.year
        country = current_app.config.get('COUNTRY_CODE', 'US')  # Default to US
        
        # Only fetch if we have an API key
        if api_key and api_key != 'your_calendarific_api_key_here':
            holidays_url = f'https://calendarific.com/api/v2/holidays?api_key={api_key}&country={country}&year={year}'
            response = requests.get(holidays_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('meta', {}).get('code') == 200:
                    holidays = data.get('response', {}).get('holidays', [])
                    
                    for holiday in holidays:
                        holiday_date = holiday.get('date', {}).get('iso')
                        if holiday_date:
                            holiday_dt = datetime.fromisoformat(holiday_date)
                            # Only include if within the requested date range
                            if start <= holiday_dt <= end:
                                events.append({
                                    'id': f'holiday_{holiday.get("name", "").replace(" ", "_")}',
                                    'title': f'🎉 {holiday.get("name", "Holiday")}',
                                    'start': holiday_date,
                                    'allDay': True,
                                    'backgroundColor': '#e3f2fd',
                                    'borderColor': '#2196f3',
                                    'textColor': '#1976d2',
                                    'classNames': ['holiday-event'],
                                    'extendedProps': {
                                        'type': 'holiday',
                                        'description': holiday.get('description', ''),
                                        'country': holiday.get('country', {}).get('name', ''),
                                        'types': holiday.get('type', [])
                                    }
                                })
    except Exception as e:
        # Silently fail - don't break calendar if holiday API fails
        print(f"Failed to fetch holidays: {str(e)}")
    
    return jsonify(events)


@bp.route('/notifications')
@login_required
def notifications():
    """All notifications"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagination = current_user.notifications.order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    items = list(pagination.items)
    unread = [n for n in items if not n.is_read]

    return render_template(
        'dashboard/notifications.html',
        pagination=pagination,
        all_notifications=items,
        unread_notifications=unread
    )


@bp.route('/notifications/<int:notif_id>/mark-read', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    """Mark notification as read"""
    notif = Notification.query.get_or_404(notif_id)
    
    if notif.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notif.mark_as_read()
    db.session.commit()
    
    return jsonify({'success': True})


@bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    current_user.notifications.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'success': True})
