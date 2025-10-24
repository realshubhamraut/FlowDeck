"""
User Blueprint - User profile and settings
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User
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

