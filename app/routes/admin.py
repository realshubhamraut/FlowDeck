"""
Admin Blueprint - Organisation and user management
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Task
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
def index():
    """Minimal admin dashboard"""
    stats = {
        'total_users': User.query.count(),
        'total_tasks': Task.query.count(),
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users)


@bp.route('/organisation', methods=['GET', 'POST'])
@login_required
def organisation():
    """Manage organisation settings"""
    org = current_user.organisation
    
    if request.method == 'POST':
        org.name = request.form.get('name', org.name)
        org.email = request.form.get('email', org.email)
        org.contact = request.form.get('contact', org.contact)
        org.color_palette = request.form.get('color_palette', org.color_palette)
        org.theme = request.form.get('theme', org.theme)
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"org_{org.id}_{timestamp}_{filename}"
                logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logos', filename)
                file.save(logo_path)
                org.logo = f"/static/uploads/logos/{filename}"
        
        db.session.commit()
        flash('Organisation settings updated successfully!', 'success')
        return redirect(url_for('admin.organisation'))
    
    return render_template('admin/organisation.html', organisation=org)


@bp.route('/users')
@login_required
def users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    users_query = User.query
    search = request.args.get('search')
    if search:
        users_query = users_query.filter(
            db.or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.designation.ilike(f'%{search}%')
            )
        )
        return redirect(url_for('admin.departments'))
    
    if request.method == 'POST':
        dept.name = request.form.get('name', dept.name)
        dept.description = request.form.get('description', dept.description)
        dept.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash(f'Department "{dept.name}" updated successfully!', 'success')
        return redirect(url_for('admin.departments'))
    
    return render_template('admin/edit_department.html', department=dept)


@bp.route('/roles')
@login_required
def roles():
    """List all roles"""
    all_roles = Role.query.all()
    return render_template('admin/roles.html', roles=all_roles)


@bp.route('/analytics')
@login_required
def analytics():
    """Organisation analytics dashboard"""
    from app.database import get_user_productivity_stats, calculate_department_completion_percentage
    
    org = current_user.organisation
    
    # Get organisation-wide statistics
    from sqlalchemy import text
    stats = db.session.execute(text("""
        SELECT 
            COUNT(DISTINCT d.id) as total_departments,
            COUNT(DISTINCT u.id) as total_users,
            COUNT(DISTINCT t.id) as total_tasks,
            COUNT(DISTINCT CASE WHEN t.status = 'done' THEN t.id END) as completed_tasks,
            COUNT(DISTINCT CASE WHEN t.status = 'in_progress' THEN t.id END) as in_progress_tasks
        FROM organisations o
        LEFT JOIN departments d ON o.id = d.organisation_id
        LEFT JOIN users u ON o.id = u.organisation_id AND u.is_active = 1
        LEFT JOIN tasks t ON d.id = t.department_id
        WHERE o.id = :org_id
    """), {'org_id': org.id}).fetchone()
    
    # Get department efficiency
    dept_stats = db.session.execute(text("""
        SELECT * FROM department_efficiency WHERE organisation_id = :org_id
    """), {'org_id': org.id}).fetchall()
    
    # Get top performers
    top_users = db.session.execute(text("""
        SELECT * FROM user_productivity_summary 
        ORDER BY completed_tasks DESC, completion_percentage DESC
        LIMIT 10
    """)).fetchall()
    
    return render_template('admin/analytics.html',
                         stats=stats,
                         dept_stats=dept_stats,
                         top_users=top_users)


# Helper functions
