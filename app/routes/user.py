"""
User Blueprint - User profile and settings
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, LeaveRequest
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import secrets

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/profile')
@login_required
def profile():
    """View user profile with optimized queries"""
    # Eager load relationships to avoid N+1 queries
    from sqlalchemy.orm import joinedload
    from app.models.task import Task
    
    user = db.session.query(User).options(
        joinedload(User.department),
        joinedload(User.organisation),
        joinedload(User.roles),
        joinedload(User.tags)
    ).filter_by(id=current_user.id).first()
    
    # Get recent tasks separately (sorted by updated_at)
    recent_tasks = db.session.query(Task).join(
        Task.assignees
    ).filter(
        User.id == current_user.id
    ).order_by(Task.updated_at.desc()).limit(5).all()
    
    return render_template('user/profile.html', user=user, recent_tasks=recent_tasks)


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.bio = request.form.get('bio', current_user.bio)
        current_user.designation = request.form.get('designation', current_user.designation)
        
        # Social links
        current_user.linkedin = request.form.get('linkedin', '').strip()
        current_user.twitter = request.form.get('twitter', '').strip()
        current_user.github = request.form.get('github', '').strip()
        
        # Profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"user_{current_user.id}_{timestamp}_{filename}"
                profile_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', filename)
                file.save(profile_path)
                current_user.profile_picture = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('user/edit_profile.html')


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings"""
    if request.method == 'POST':
        current_user.theme_preference = request.form.get('theme', 'light')
        current_user.notification_enabled = request.form.get('notifications') == 'on'
        current_user.email_notification_enabled = request.form.get('email_notifications') == 'on'
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('user.settings'))
    
    return render_template('user/settings.html')


@bp.route('/leave-requests')
@login_required
def leave_requests():
    """View leave requests"""
    page = request.args.get('page', 1, type=int)
    pagination = current_user.leave_requests.order_by(
        LeaveRequest.requested_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('user/leave_requests.html', pagination=pagination)


@bp.route('/leave-requests/create', methods=['GET', 'POST'])
@login_required
def create_leave_request():
    """Create leave request"""
    if request.method == 'POST':
        leave_type = request.form.get('leave_type')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        reason = request.form.get('reason', '').strip()
        
        if not all([leave_type, start_date_str, end_date_str, reason]):
            flash('All fields are required.', 'warning')
            return render_template('user/create_leave_request.html')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('user/create_leave_request.html')
        
        if end_date < start_date:
            flash('End date must be after start date.', 'warning')
            return render_template('user/create_leave_request.html')
        
        leave_request = LeaveRequest(
            user_id=current_user.id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        leave_request.calculate_days()
        
        # Handle supporting document upload
        if 'supporting_document' in request.files:
            file = request.files['supporting_document']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"leave_{current_user.id}_{timestamp}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attachments', filename)
                file.save(file_path)
                leave_request.supporting_document = f"/static/uploads/attachments/{filename}"
        
        db.session.add(leave_request)
        db.session.commit()
        
        # Notify manager
        if current_user.department and current_user.department.users.filter_by(is_active=True).first():
            # Find manager in department
            from app.models import Notification, Role
            manager_role = Role.query.filter_by(name='Manager').first()
            if manager_role:
                managers = User.query.join(User.roles).filter(
                    Role.id == manager_role.id,
                    User.department_id == current_user.department_id
                ).all()
                
                for manager in managers:
                    notif = Notification(
                        user_id=manager.id,
                        title='New Leave Request',
                        message=f'{current_user.name} requested leave from {start_date} to {end_date}',
                        notification_type='leave_request',
                        action_url=f'/user/leave-requests/{leave_request.id}'
                    )
                    db.session.add(notif)
        
        db.session.commit()
        
        flash('Leave request submitted successfully!', 'success')
        return redirect(url_for('user.leave_requests'))
    
    return render_template('user/create_leave_request.html')


@bp.route('/<int:user_id>/view')
@login_required
def view_user(user_id):
    """View other user's profile"""
    user = User.query.get_or_404(user_id)
    
    # Check same organisation
    if user.organisation_id != current_user.organisation_id:
        flash('User not found.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('user/view_user.html', user=user)


@bp.route('/resend-verification', methods=['POST'])
@login_required
def resend_verification():
    """Resend email verification link"""
    if current_user.is_email_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('user.profile'))
    
    # Generate new verification token
    token = secrets.token_urlsafe(32)
    current_user.email_verification_token = token
    db.session.commit()
    
    # Send verification email
    try:
        from app.utils.email import send_verification_email
        verification_url = url_for('auth.verify_email', token=token, _external=True)
        send_verification_email(current_user.email, current_user.name, verification_url)
        flash('Verification email sent! Please check your inbox.', 'success')
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email: {e}")
        flash('Failed to send verification email. Please try again later.', 'danger')
    
    return redirect(url_for('user.profile'))

