"""
Meetings Blueprint - Meeting scheduling and management
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Meeting, User, Task

from app.routes.auth import manager_required
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json

bp = Blueprint('meetings', __name__, url_prefix='/meetings')


def can_access_meeting(meeting):
    """Check if current user can access a meeting"""
    if current_user.is_admin():
        return True
    if meeting.organizer_id == current_user.id:
        return True
    if current_user in meeting.attendees:
        return True
    return False




def get_users():
    """Get users for attendee selection"""
    if current_user.is_admin():
        return User.query.filter_by(is_active=True).order_by(User.name).all()
    elif current_user.is_manager() and current_user.department:
        return User.query.filter_by(
            department_id=current_user.department_id,
            is_active=True
        ).order_by(User.name).all()
    return User.query.filter_by(is_active=True).order_by(User.name).all()


@bp.route('/')
@bp.route('/list')
@login_required
def list_meetings():
    """List all meetings"""
    view = request.args.get('view', 'upcoming')  # upcoming, past, all
    
    # Base query - meetings user organized or attending
    if current_user.is_admin():
        meetings_query = Meeting.query
    else:
        meetings_query = Meeting.query.filter(
            db.or_(
                Meeting.organizer_id == current_user.id,
                Meeting.attendees.any(id=current_user.id)
            )
        )
    
    # Apply view filter
    now = datetime.utcnow()
    if view == 'upcoming':
        meetings_query = meetings_query.filter(
            Meeting.start_time > now,
            Meeting.status != 'cancelled'
        ).order_by(Meeting.start_time.asc())
    elif view == 'past':
        meetings_query = meetings_query.filter(
            db.or_(
                Meeting.end_time < now,
                Meeting.status.in_(['completed', 'cancelled'])
            )
        ).order_by(Meeting.start_time.desc())
    else:  # all
        meetings_query = meetings_query.order_by(Meeting.start_time.desc())
    
    # Apply additional filters
    status = request.args.get('status')
    if status:
        meetings_query = meetings_query.filter_by(status=status)
    
    meeting_type = request.args.get('type')
    if meeting_type:
        meetings_query = meetings_query.filter_by(meeting_type=meeting_type)
    
    search = request.args.get('search')
    if search:
        meetings_query = meetings_query.filter(
            db.or_(
                Meeting.title.ilike(f'%{search}%'),
                Meeting.description.ilike(f'%{search}%')
            )
        )
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    pagination = meetings_query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template(
        'meetings/list.html',
        pagination=pagination,
        meetings=pagination.items,
        view=view
    )


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_meeting():
    """Create new meeting"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        meeting_type = request.form.get('meeting_type', 'general')
        location = request.form.get('location', '').strip()
        meeting_link = request.form.get('meeting_link', '').strip()
        priority = request.form.get('priority', 'normal')
        is_private = request.form.get('is_private') == 'on'
        
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        department_id = request.form.get('department_id')
        task_id = request.form.get('task_id')
        attendee_ids = request.form.getlist('attendees')
        
        # Agenda items
        agenda_json = request.form.get('agenda')
        
        # Validation
        if not title:
            flash('Meeting title is required.', 'warning')
            return render_template('meetings/create.html',
                                 users=get_users(),
                                 tasks=Task.query.filter_by(status='in_progress').all())
        
        # Parse start time
        start_time = None
        if start_time_str:
            try:
                start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid start time format.', 'warning')
                return redirect(url_for('meetings.create_meeting'))
        
        # Parse end time
        end_time = None
        if end_time_str:
            try:
                end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid end time format.', 'warning')
                return redirect(url_for('meetings.create_meeting'))
        
        # Validate times
        if not start_time or not end_time:
            flash('Start time and end time are required.', 'warning')
            return redirect(url_for('meetings.create_meeting'))
        
        if start_time >= end_time:
            flash('End time must be after start time.', 'warning')
            return redirect(url_for('meetings.create_meeting'))
        
        # Create meeting
        meeting = Meeting(
            title=title,
            description=description,
            meeting_type=meeting_type,
            location=location,
            meeting_link=meeting_link,
            start_time=start_time,
            end_time=end_time,
            priority=priority,
            is_private=is_private,
            task_id=task_id if task_id else None,
            organizer_id=current_user.id
        )
        
        db.session.add(meeting)
        db.session.flush()
        
        # Add attendees
        if attendee_ids:
            attendee_ids = [int(aid) for aid in attendee_ids if aid]
            attendees = User.query.filter(User.id.in_(attendee_ids)).all()
            meeting.attendees.extend(attendees)
        
        # Add agenda items
        
        db.session.commit()
        
        # Handle file attachments
        
        # Create notifications for attendees
        
        flash(f'Meeting "{meeting.title}" created successfully!', 'success')
        return redirect(url_for('meetings.view_meeting', meeting_id=meeting.id))
    
    return render_template('meetings/create.html',
                         users=get_users(),
                         tasks=Task.query.filter(Task.status.in_(['todo', 'in_progress'])).all())


@bp.route('/<int:meeting_id>')
@login_required
def view_meeting(meeting_id):
    """View meeting details"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if not can_access_meeting(meeting):
        flash('You do not have permission to view this meeting.', 'danger')
        return redirect(url_for('meetings.list_meetings'))
    
    return render_template('meetings/view.html', meeting=meeting)


@bp.route('/<int:meeting_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_meeting(meeting_id):
    """Edit meeting"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Only organizer or admin can edit
    if meeting.organizer_id != current_user.id and not current_user.is_admin():
        flash('Only the organizer can edit this meeting.', 'danger')
        return redirect(url_for('meetings.view_meeting', meeting_id=meeting_id))
    
    if request.method == 'POST':
        meeting.title = request.form.get('title', '').strip()
        meeting.description = request.form.get('description', '').strip()
        meeting.meeting_type = request.form.get('meeting_type', 'general')
        meeting.location = request.form.get('location', '').strip()
        meeting.meeting_link = request.form.get('meeting_link', '').strip()
        meeting.priority = request.form.get('priority', 'normal')
        meeting.is_private = request.form.get('is_private') == 'on'
        meeting.status = request.form.get('status', 'scheduled')
        
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        if start_time_str:
            try:
                meeting.start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        
        if end_time_str:
            try:
                meeting.end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        
        # Update attendees
        attendee_ids = request.form.getlist('attendees')
        if attendee_ids:
            attendee_ids = [int(aid) for aid in attendee_ids if aid]
            meeting.attendees = User.query.filter(User.id.in_(attendee_ids)).all()
        
        # Update agenda
        
        db.session.commit()
        
        # Handle new file attachments
        
        flash('Meeting updated successfully!', 'success')
        return redirect(url_for('meetings.view_meeting', meeting_id=meeting_id))
    
    return render_template('meetings/edit.html',
                         meeting=meeting,
                         users=get_users(),
                         tasks=Task.query.filter(Task.status.in_(['todo', 'in_progress'])).all())


@bp.route('/<int:meeting_id>/respond', methods=['POST'])
@login_required
def respond_to_meeting(meeting_id):
    """Respond to meeting invitation"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if current_user not in meeting.attendees:
        return jsonify({'error': 'You are not invited to this meeting'}), 403
    
    response = request.json.get('response')  # accepted, declined, tentative
    
    if response not in ['accepted', 'declined', 'tentative']:
        return jsonify({'error': 'Invalid response'}), 400
    
    # Update attendance status
    # Minimal version: just commit, no attendance table
    db.session.commit()
    
    return jsonify({'success': True, 'response': response})


@bp.route('/<int:meeting_id>/delete', methods=['POST'])
@login_required
def delete_meeting(meeting_id):
    """Delete meeting"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Only organizer or admin can delete
    if meeting.organizer_id != current_user.id and not current_user.is_admin():
        flash('Only the organizer can delete this meeting.', 'danger')
        return redirect(url_for('meetings.view_meeting', meeting_id=meeting_id))
    
    title = meeting.title
    db.session.delete(meeting)
    db.session.commit()
    
    flash(f'Meeting "{title}" deleted successfully.', 'success')
    return redirect(url_for('meetings.list_meetings'))
