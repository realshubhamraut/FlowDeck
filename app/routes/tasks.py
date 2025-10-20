"""
Tasks Blueprint - Task and project management
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Task, TaskComment, TaskAttachment, TimeLog, User, Department, Tag, Notification
from app.routes.auth import manager_required
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@bp.route('/')
@bp.route('/list')
@login_required
def list_tasks():
    """List all tasks"""
    view = request.args.get('view', 'list')  # list or kanban
    
    # Base query
    if current_user.is_manager():
        # Managers see all department tasks
        tasks_query = Task.query.filter_by(department_id=current_user.department_id)
    else:
        # Users see only their assigned tasks
        tasks_query = current_user.assigned_tasks
    
    # Apply filters
    status = request.args.get('status')
    if status:
        tasks_query = tasks_query.filter_by(status=status)
    
    priority = request.args.get('priority')
    if priority:
        tasks_query = tasks_query.filter_by(priority=priority)
    
    department_id = request.args.get('department')
    if department_id and current_user.is_admin():
        tasks_query = Task.query.filter_by(department_id=department_id)
    
    search = request.args.get('search')
    if search:
        tasks_query = tasks_query.filter(
            db.or_(
                Task.title.ilike(f'%{search}%'),
                Task.description.ilike(f'%{search}%')
            )
        )
    
    # Sort
    sort = request.args.get('sort', 'due_date')
    sort_order = request.args.get('sort_order', 'asc')  # 'asc' or 'desc'
    
    # Determine sort direction
    desc_order = (sort_order == 'desc')
    
    # Apply sorting based on field
    if sort == 'priority':
        # Priority mapping: urgent=4, high=3, medium=2, low=1
        priority_order = db.case(
            (Task.priority == 'urgent', 4),
            (Task.priority == 'high', 3),
            (Task.priority == 'medium', 2),
            (Task.priority == 'low', 1),
            else_=0
        )
        tasks_query = tasks_query.order_by(priority_order.desc() if desc_order else priority_order.asc())
    elif sort == 'status':
        # Status mapping: todo=1, in_progress=2, done=3, archived=4
        status_order = db.case(
            (Task.status == 'todo', 1),
            (Task.status == 'in_progress', 2),
            (Task.status == 'done', 3),
            (Task.status == 'archived', 4),
            else_=0
        )
        tasks_query = tasks_query.order_by(status_order.desc() if desc_order else status_order.asc())
    elif sort == 'title':
        tasks_query = tasks_query.order_by(Task.title.desc() if desc_order else Task.title.asc())
    elif sort == 'due_date':
        tasks_query = tasks_query.order_by(Task.due_date.desc() if desc_order else Task.due_date.asc())
    elif sort == 'created':
        tasks_query = tasks_query.order_by(Task.created_at.desc() if desc_order else Task.created_at.asc())
    else:
        # Default to due_date ascending
        tasks_query = tasks_query.order_by(Task.due_date.asc())
    
    if view == 'kanban':
        tasks = tasks_query.all()
        # Group by status for kanban
        tasks_by_status = {
            'todo': [t for t in tasks if t.status == 'todo'],
            'in_progress': [t for t in tasks if t.status == 'in_progress'],
            'done': [t for t in tasks if t.status == 'done']
        }
        return render_template('tasks/kanban.html', tasks_by_status=tasks_by_status)
    else:
        page = request.args.get('page', 1, type=int)
        pagination = tasks_query.paginate(page=page, per_page=20, error_out=False)
        # Compute quick counts for header cards
        try:
            base = tasks_query
            total_count = base.count()
            todo_count = base.filter_by(status='todo').count()
            in_progress_count = base.filter_by(status='in_progress').count()
            done_count = base.filter_by(status='done').count()
        except Exception:
            total_count = len(pagination.items)
            todo_count = len([t for t in pagination.items if getattr(t, 'status', None) == 'todo'])
            in_progress_count = len([t for t in pagination.items if getattr(t, 'status', None) == 'in_progress'])
            done_count = len([t for t in pagination.items if getattr(t, 'status', None) == 'done'])

        return render_template(
            'tasks/list.html',
            pagination=pagination,
            tasks=pagination,  # template expects tasks iterable and pagination methods
            total_count=total_count,
            todo_count=todo_count,
            in_progress_count=in_progress_count,
            done_count=done_count,
            can_edit_task=can_edit_task
        )


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_task():
    """Create new task"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        status = request.form.get('status', 'todo')
        department_id = request.form.get('department_id')
        start_date_str = request.form.get('start_date')
        due_date_str = request.form.get('due_date')
        estimated_hours = request.form.get('estimated_hours', type=float)
        assignee_ids = request.form.getlist('assignees')
        tag_ids = request.form.getlist('tags')
        
        # Deliverables
        deliverables_json = request.form.get('deliverables')
        
        # Validation
        if not title:
            flash('Task title is required.', 'warning')
            return render_template('tasks/create.html',
                                 departments=get_departments(),
                                 users=get_users(),
                                 tags=Tag.query.all())
        
        # Parse start date
        start_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
        
        # Parse due date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
        
        # Validate that start_date is before due_date
        if start_date and due_date and start_date > due_date:
            flash('Start date cannot be after due date.', 'warning')
            return render_template('tasks/create.html',
                                 departments=get_departments(),
                                 users=get_users(),
                                 tags=Tag.query.all())
        
        # Create task
        task = Task(
            title=title,
            description=description,
            priority=priority,
            status=status,
            department_id=department_id if department_id else current_user.department_id,
            start_date=start_date,
            due_date=due_date,
            estimated_hours=estimated_hours,
            created_by_id=current_user.id
        )
        
        # Set deliverables
        if deliverables_json:
            try:
                deliverables = json.loads(deliverables_json)
                task.set_deliverables(deliverables)
            except:
                pass
        
        db.session.add(task)
        db.session.flush()
        
        # Assign users
        if assignee_ids:
            # Convert string IDs to integers
            assignee_ids = [int(aid) for aid in assignee_ids if aid]
            assignees = User.query.filter(User.id.in_(assignee_ids)).all()
            task.assignees.extend(assignees)
        
        # Assign tags
        if tag_ids:
            # Convert string IDs to integers
            tag_ids = [int(tid) for tid in tag_ids if tid]
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            task.tags.extend(tags)
        
        # Commit task and relationships first
        db.session.commit()
        
        # Now create notifications for assignees (after commit)
        if assignee_ids:
            for assignee_id in assignee_ids:
                notif = Notification(
                    user_id=assignee_id,
                    title='New Task Assigned',
                    message=f'You have been assigned to: {task.title}',
                    notification_type='task_assigned',
                    task_id=task.id,
                    action_url=f'/tasks/{task.id}'
                )
                db.session.add(notif)
            db.session.commit()
        
        flash(f'Task "{task.title}" created successfully!', 'success')
        return redirect(url_for('tasks.view_task', task_id=task.id))
    
    return render_template('tasks/create.html',
                         departments=get_departments(),
                         users=get_users(),
                         tags=Tag.query.all())


@bp.route('/<int:task_id>')
@login_required
def view_task(task_id):
    """View task details"""
    task = Task.query.get_or_404(task_id)
    
    # Check access
    if not can_access_task(task):
        flash('You do not have permission to view this task.', 'danger')
        return redirect(url_for('tasks.list_tasks'))
    
    # Get comments with user info
    comments = task.comments.all()
    
    # Get attachments
    attachments = task.attachments.all()
    
    # Get time logs
    time_logs = task.time_logs.order_by(TimeLog.start_time.desc()).all()
    
    # Get task history
    from app.models import TaskHistory
    history = TaskHistory.query.filter_by(task_id=task.id).order_by(
        TaskHistory.created_at.desc()
    ).limit(20).all()
    
    return render_template('tasks/view.html',
                         task=task,
                         comments=comments,
                         attachments=attachments,
                         time_logs=time_logs,
                         history=history)


@bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit task"""
    task = Task.query.get_or_404(task_id)
    
    # Check permission
    if not can_edit_task(task):
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('tasks.view_task', task_id=task_id))
    
    if request.method == 'POST':
        # Store old values for history
        old_status = task.status
        
        task.title = request.form.get('title', task.title)
        task.description = request.form.get('description', task.description)
        task.priority = request.form.get('priority', task.priority)
        task.status = request.form.get('status', task.status)
        task.department_id = request.form.get('department_id') or task.department_id
        
        # Update start date
        start_date_str = request.form.get('start_date')
        if start_date_str:
            try:
                task.start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    task.start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
        
        # Update due date
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
        
        # Validate that start_date is before due_date
        if task.start_date and task.due_date and task.start_date > task.due_date:
            flash('Start date cannot be after due date.', 'warning')
            return render_template('tasks/edit.html',
                                 task=task,
                                 departments=get_departments(),
                                 users=get_users(),
                                 tags=Tag.query.all())
        
        task.estimated_hours = request.form.get('estimated_hours', type=float) or task.estimated_hours
        
        # Update deliverables
        deliverables_json = request.form.get('deliverables')
        if deliverables_json:
            try:
                deliverables = json.loads(deliverables_json)
                task.set_deliverables(deliverables)
            except:
                pass
        
        # Update assignees
        assignee_ids = request.form.getlist('assignees')
        if assignee_ids:
            task.assignees = User.query.filter(User.id.in_(assignee_ids)).all()
        
        # Update tags
        tag_ids = request.form.getlist('tags')
        if tag_ids:
            task.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        
        # Log history if status changed
        if old_status != task.status:
            from app.models import TaskHistory
            history = TaskHistory(
                task_id=task.id,
                user_id=current_user.id,
                action='status_changed',
                field_changed='status',
                old_value=old_status,
                new_value=task.status
            )
            db.session.add(history)
            
            # Notify assignees about status change
            for assignee in task.assignees:
                notif = Notification(
                    user_id=assignee.id,
                    title='Task Status Updated',
                    message=f'Task "{task.title}" status changed to {task.status}',
                    notification_type='task_updated',
                    task_id=task.id,
                    action_url=f'/tasks/{task.id}'
                )
                db.session.add(notif)
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.view_task', task_id=task_id))
    
    return render_template('tasks/edit.html',
                         task=task,
                         departments=get_departments(),
                         users=get_users(),
                         tags=Tag.query.all())


@bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
@manager_required
def delete(task_id):
    """Delete task"""
    task = Task.query.get_or_404(task_id)
    
    if not can_edit_task(task):
        return jsonify({'error': 'Unauthorized'}), 403
    
    title = task.title
    db.session.delete(task)
    db.session.commit()
    
    flash(f'Task "{title}" deleted successfully.', 'info')
    return redirect(url_for('tasks.list_tasks'))


@bp.route('/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_status(task_id):
    """Update task status (AJAX)"""
    task = Task.query.get_or_404(task_id)
    
    if not can_access_task(task):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['todo', 'in_progress', 'done', 'archived']:
        return jsonify({'error': 'Invalid status'}), 400
    
    old_status = task.status
    task.status = new_status
    
    if new_status == 'done' and not task.completed_date:
        task.completed_date = datetime.utcnow()
    
    # Log history
    from app.models import TaskHistory
    history = TaskHistory(
        task_id=task.id,
        user_id=current_user.id,
        action='status_changed',
        field_changed='status',
        old_value=old_status,
        new_value=new_status
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify({'success': True, 'status': new_status})


@bp.route('/<int:task_id>/comment', methods=['POST'])
@login_required
def add_comment(task_id):
    """Add comment to task"""
    task = Task.query.get_or_404(task_id)
    
    if not can_access_task(task):
        return jsonify({'error': 'Unauthorized'}), 403
    
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Comment cannot be empty.', 'warning')
        return redirect(url_for('tasks.view_task', task_id=task_id))
    
    comment = TaskComment(
        content=content,
        task_id=task_id,
        user_id=current_user.id
    )
    db.session.add(comment)
    db.session.commit()
    
    # Notify task creator and assignees
    notify_users = set([task.creator] + task.assignees.all())
    notify_users.discard(current_user)  # Don't notify self
    
    for user in notify_users:
        if user:
            notif = Notification(
                user_id=user.id,
                title='New Comment on Task',
                message=f'{current_user.name} commented on: {task.title}',
                notification_type='comment_added',
                task_id=task.id,
                action_url=f'/tasks/{task.id}'
            )
            db.session.add(notif)
    
    db.session.commit()
    
    flash('Comment added successfully!', 'success')
    return redirect(url_for('tasks.view_task', task_id=task_id))


@bp.route('/<int:task_id>/upload', methods=['POST'])
@login_required
def upload_attachment(task_id):
    """Upload file attachment"""
    task = Task.query.get_or_404(task_id)
    
    if not can_access_task(task):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        flash('No file selected.', 'warning')
        return redirect(url_for('tasks.view_task', task_id=task_id))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected.', 'warning')
        return redirect(url_for('tasks.view_task', task_id=task_id))
    
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"task_{task_id}_{timestamp}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attachments', unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        attachment = TaskAttachment(
            filename=unique_filename,
            original_filename=filename,
            file_path=f"/static/uploads/attachments/{unique_filename}",
            file_size=file_size,
            mime_type=file.content_type,
            task_id=task_id,
            uploaded_by_id=current_user.id
        )
        db.session.add(attachment)
        db.session.commit()
        
        flash('File uploaded successfully!', 'success')
    
    return redirect(url_for('tasks.view_task', task_id=task_id))


@bp.route('/<int:task_id>/time-log', methods=['POST'])
@login_required
def add_time_log(task_id):
    """Add time log entry"""
    task = Task.query.get_or_404(task_id)
    
    if not can_access_task(task):
        return jsonify({'error': 'Unauthorized'}), 403
    
    duration = request.form.get('duration', type=float)
    notes = request.form.get('notes', '').strip()
    
    if not duration or duration <= 0:
        flash('Please enter a valid duration.', 'warning')
        return redirect(url_for('tasks.view_task', task_id=task_id))
    
    time_log = TimeLog(
        task_id=task_id,
        user_id=current_user.id,
        duration=duration,
        notes=notes
    )
    db.session.add(time_log)
    db.session.commit()
    
    flash('Time log added successfully!', 'success')
    return redirect(url_for('tasks.view_task', task_id=task_id))


# Helper functions
def can_access_task(task):
    """Check if user can access task"""
    if current_user.is_admin():
        return True
    if current_user.is_manager() and task.department_id == current_user.department_id:
        return True
    if current_user in task.assignees:
        return True
    if task.created_by_id == current_user.id:
        return True
    return False


def can_edit_task(task):
    """Check if user can edit task"""
    if current_user.is_manager():
        return True
    if task.created_by_id == current_user.id:
        return True
    return False


def get_departments():
    """Get departments for current organisation"""
    return Department.query.filter_by(
        organisation_id=current_user.organisation_id,
        is_active=True
    ).order_by(Department.name).all()


def get_users():
    """Get users for task assignment"""
    if current_user.is_admin():
        return User.query.filter_by(
            organisation_id=current_user.organisation_id,
            is_active=True
        ).order_by(User.name).all()
    elif current_user.is_manager():
        return User.query.filter_by(
            department_id=current_user.department_id,
            is_active=True
        ).order_by(User.name).all()
    return []
