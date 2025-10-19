"""
Admin Blueprint - Organisation and user management
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Organisation, Department, User, Role, Tag, AuditLog, Task
from app.routes.auth import admin_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    org = current_user.organisation
    
    stats = {
        'total_users': User.query.filter_by(organisation_id=org.id, is_active=True).count(),
        'total_departments': Department.query.filter_by(organisation_id=org.id, is_active=True).count(),
        'total_tasks': db.session.query(db.func.count(Task.id))
            .join(User, Task.created_by_id == User.id)
            .filter(User.organisation_id == org.id)
            .scalar() or 0,
    }
    
    recent_users = User.query.filter_by(organisation_id=org.id).order_by(
        User.created_at.desc()
    ).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users)


@bp.route('/organisation', methods=['GET', 'POST'])
@login_required
@admin_required
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
@admin_required
def users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    users_query = User.query.filter_by(organisation_id=current_user.organisation_id)
    
    # Apply filters
    department_id = request.args.get('department')
    if department_id:
        users_query = users_query.filter_by(department_id=department_id)
    
    search = request.args.get('search')
    if search:
        users_query = users_query.filter(
            db.or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.designation.ilike(f'%{search}%')
            )
        )
    
    pagination = users_query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    departments = Department.query.filter_by(
        organisation_id=current_user.organisation_id, is_active=True
    ).all()
    
    return render_template('admin/users.html', 
                         pagination=pagination, 
                         departments=departments)


@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create new user"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        designation = request.form.get('designation', '').strip()
        date_of_birth_str = request.form.get('date_of_birth', '').strip()
        department_id = request.form.get('department_id')
        role_ids = request.form.getlist('roles')
        tag_ids = request.form.getlist('tags')
        
        # Parse date of birth
        date_of_birth = None
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Social links
        linkedin = request.form.get('linkedin', '').strip()
        twitter = request.form.get('twitter', '').strip()
        github = request.form.get('github', '').strip()
        
        # Validation
        if not name or not email:
            flash('Name and email are required.', 'warning')
            return render_template('admin/create_user.html', 
                                 departments=get_departments(),
                                 roles=get_roles(),
                                 tags=get_tags())
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'danger')
            return render_template('admin/create_user.html',
                                 departments=get_departments(),
                                 roles=get_roles(),
                                 tags=get_tags())
        
        # Generate random password
        password = User.generate_random_password()
        
        # Create user
        user = User(
            name=name,
            email=email,
            phone=phone,
            designation=designation,
            date_of_birth=date_of_birth,
            department_id=department_id if department_id else None,
            organisation_id=current_user.organisation_id,
            linkedin=linkedin,
            twitter=twitter,
            github=github
        )
        user.set_password(password)
        
        # Generate email verification token
        verification_token = user.generate_verification_token()
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"user_{timestamp}_{filename}"
                profile_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', filename)
                file.save(profile_path)
                user.profile_picture = f"/static/uploads/profiles/{filename}"
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Assign roles
        if role_ids:
            roles = Role.query.filter(Role.id.in_(role_ids)).all()
            user.roles.extend(roles)
        
        # Assign tags
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            user.tags.extend(tags)
        
        db.session.commit()
        
        # IMPORTANT: Display password to admin (do NOT email it - email system may not be configured)
        # Store password in session for one-time display on next page
        from flask import session
        session['new_user_password'] = {
            'name': user.name,
            'email': user.email,
            'password': password
        }
        
        flash(f'User {user.name} created successfully!', 'success')
        return redirect(url_for('admin.show_new_user_credentials'))
    
    return render_template('admin/create_user.html',
                         departments=get_departments(),
                         roles=get_roles(),
                         tags=get_tags(),
                         today=datetime.now().strftime('%Y-%m-%d'))


@bp.route('/users/credentials')
@login_required
@admin_required
def show_new_user_credentials():
    """Show newly created user credentials (one-time view)"""
    from flask import session
    
    # Get credentials from session
    creds = session.pop('new_user_password', None)
    
    if not creds:
        flash('No credentials to display. Credentials can only be viewed once after user creation.', 'warning')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_credentials.html', credentials=creds)


@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    
    # Check if user belongs to same organisation
    if user.organisation_id != current_user.organisation_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('admin.users'))
    
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        user.phone = request.form.get('phone', user.phone)
        user.designation = request.form.get('designation', user.designation)
        user.department_id = request.form.get('department_id') or None
        user.is_active = request.form.get('is_active') == 'on'
        
        # Parse date of birth
        date_of_birth_str = request.form.get('date_of_birth', '').strip()
        if date_of_birth_str:
            try:
                user.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
            user.date_of_birth = None
        
        # Social links
        user.linkedin = request.form.get('linkedin', '').strip()
        user.twitter = request.form.get('twitter', '').strip()
        user.github = request.form.get('github', '').strip()
        
        # Update roles
        role_ids = request.form.getlist('roles')
        user.roles = Role.query.filter(Role.id.in_(role_ids)).all() if role_ids else []
        
        # Update tags
        tag_ids = request.form.getlist('tags')
        user.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"user_{user.id}_{timestamp}_{filename}"
                profile_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', filename)
                file.save(profile_path)
                user.profile_picture = f"/static/uploads/profiles/{filename}"
        
        db.session.commit()
        flash(f'User {user.name} updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html',
                         user=user,
                         departments=get_departments(),
                         roles=get_roles(),
                         tags=get_tags(),
                         today=datetime.now().strftime('%Y-%m-%d'))


@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    if user.organisation_id != current_user.organisation_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('admin.users'))
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'warning')
        return redirect(url_for('admin.users'))
    
    name = user.name
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {name} deleted successfully.', 'info')
    return redirect(url_for('admin.users'))


@bp.route('/departments')
@login_required
@admin_required
def departments():
    """List all departments"""
    depts = Department.query.filter_by(
        organisation_id=current_user.organisation_id
    ).order_by(Department.name).all()
    
    return render_template('admin/departments.html', departments=depts)


@bp.route('/departments/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_department():
    """Create new department"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Department name is required.', 'warning')
            return render_template('admin/create_department.html')
        
        dept = Department(
            name=name,
            description=description,
            organisation_id=current_user.organisation_id
        )
        db.session.add(dept)
        db.session.commit()
        
        # Create default chat channel for department
        from app.models import ChatChannel
        channel = ChatChannel(
            name=f"{name} - Team Chat",
            description=f"Department chat for {name}",
            channel_type='department',
            department_id=dept.id,
            organisation_id=current_user.organisation_id,
            created_by_id=current_user.id
        )
        db.session.add(channel)
        db.session.commit()
        
        flash(f'Department "{name}" created successfully!', 'success')
        return redirect(url_for('admin.departments'))
    
    return render_template('admin/create_department.html')


@bp.route('/departments/<int:dept_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(dept_id):
    """Edit department"""
    dept = Department.query.get_or_404(dept_id)
    
    if dept.organisation_id != current_user.organisation_id:
        flash('Unauthorized access.', 'danger')
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
@admin_required
def roles():
    """List all roles"""
    all_roles = Role.query.all()
    return render_template('admin/roles.html', roles=all_roles)


@bp.route('/analytics')
@login_required
@admin_required
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
def get_departments():
    """Get departments for current organisation"""
    return Department.query.filter_by(
        organisation_id=current_user.organisation_id,
        is_active=True
    ).order_by(Department.name).all()


def get_roles():
    """Get all roles"""
    return Role.query.all()


def get_tags():
    """Get all tags"""
    return Tag.query.all()
