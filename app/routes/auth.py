"""
Authentication Blueprint
Handles login, logout, registration, and email verification
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Organisation, Role, AuditLog
from werkzeug.security import generate_password_hash
from app.utils.validators import validate_password_strength, validate_email
from functools import wraps
import secrets

bp = Blueprint('auth', __name__, url_prefix='/auth')


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """Decorator to require manager or admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_manager():
            flash('You need manager privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        login_type = request.form.get('login_type', 'user')  # 'user' or 'admin'
        org_id = request.form.get('org_id', '').strip()  # Optional for admin
        
        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact your administrator.', 'danger')
                return render_template('auth/login.html')
            
            # Validate admin login
            if login_type == 'admin':
                if not user.is_admin():
                    flash('⚠️ Admin credentials required. This account does not have administrator privileges.', 'danger')
                    return render_template('auth/login.html')
                
                # If org_id is provided, verify user belongs to that organization
                if org_id:
                    try:
                        org_id_int = int(org_id)
                        if user.organisation_id != org_id_int:
                            flash('Invalid organization ID for this admin account.', 'danger')
                            return render_template('auth/login.html')
                    except ValueError:
                        flash('Invalid organization ID format.', 'warning')
                        return render_template('auth/login.html')
                
                flash(f'✅ Welcome back, Admin {user.name}!', 'success')
            else:
                flash(f'👋 Welcome back, {user.name}!', 'success')
            
            # Log the user in
            login_user(user, remember=remember)
            
            # Update last login
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log audit with login type
            log_audit(user.id, user.organisation_id, 'user_login', 'User', user.id, 
                     f'{login_type.capitalize()} login: {user.email}')
            
            # Redirect to next page or appropriate dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirect admin users to admin dashboard if they logged in as admin
            if login_type == 'admin' and user.is_admin():
                return redirect(url_for('admin.index'))
            
            return redirect(url_for('dashboard.index'))
        else:
            if login_type == 'admin':
                flash('❌ Invalid admin credentials. Please check your email and password.', 'danger')
            else:
                flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    user_id = current_user.id
    org_id = current_user.organisation_id
    
    # Log audit
    log_audit(user_id, org_id, 'user_logout', 'User', user_id, f'User logged out')
    
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify user email with token"""
    user = User.query.filter_by(email_verification_token=token).first()
    
    if not user:
        flash('Invalid or expired verification token.', 'danger')
        return redirect(url_for('auth.login'))
    
    user.is_email_verified = True
    user.email_verification_token = None
    db.session.commit()
    
    flash('Your email has been verified successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please provide your email address.', 'warning')
            return render_template('auth/forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.email_verification_token = reset_token  # Reusing field for simplicity
            db.session.commit()
            
            # Send reset email
            from app.utils.email import send_password_reset_email
            send_password_reset_email(user, reset_token)
            
        # Always show success message (security best practice)
        flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    user = User.query.filter_by(email_verification_token=token).first()
    
    if not user:
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate password strength
        password_valid, password_error = validate_password_strength(password)
        if not password_valid:
            flash(f'Weak password: {password_error}', 'warning')
            return render_template('auth/reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return render_template('auth/reset_password.html', token=token)
        
        user.set_password(password)
        user.email_verification_token = None
        db.session.commit()
        
        flash('Your password has been reset successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Public registration - Create organization and admin user"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Organization details
        org_name = request.form.get('name', '').strip()
        org_email = request.form.get('email', '').strip().lower()
        org_contact = request.form.get('contact', '').strip()
        
        # Admin user details
        admin_name = request.form.get('admin_name', '').strip()
        admin_email = request.form.get('admin_email', '').strip().lower()
        admin_password = request.form.get('admin_password', '')
        
        # Validation
        if not org_name or not org_email:
            flash('Organization name and email are required.', 'warning')
            return render_template('auth/register.html')
        
        if not admin_name or not admin_email or not admin_password:
            flash('Admin name, email, and password are required.', 'warning')
            return render_template('auth/register.html')
        
        # Validate email format
        email_valid, email_error = validate_email(admin_email)
        if not email_valid:
            flash(f'Invalid admin email: {email_error}', 'warning')
            return render_template('auth/register.html')
        
        # Validate password strength
        password_valid, password_error = validate_password_strength(admin_password)
        if not password_valid:
            flash(f'Weak password: {password_error}', 'warning')
            return render_template('auth/register.html')
        
        # Check if organization already exists
        if Organisation.query.filter_by(email=org_email).first():
            flash('An organization with this email already exists.', 'danger')
            return render_template('auth/register.html')
        
        # Check if admin email already exists
        if User.query.filter_by(email=admin_email).first():
            flash('A user with this email already exists.', 'danger')
            return render_template('auth/register.html')
        
        try:
            # Create organization
            organisation = Organisation(
                name=org_name,
                email=org_email,
                contact=org_contact,
                is_active=True
            )
            db.session.add(organisation)
            db.session.flush()  # Get the org ID
            
            # Get or create Admin role
            admin_role = Role.query.filter_by(name='Admin').first()
            if not admin_role:
                admin_role = Role(name='Admin', description='Administrator with full access')
                db.session.add(admin_role)
                db.session.flush()
            
            # Create admin user
            admin_user = User(
                name=admin_name,
                email=admin_email,
                organisation_id=organisation.id,
                is_active=True,
                is_email_verified=True  # Auto-verify for initial setup
            )
            admin_user.set_password(admin_password)
            admin_user.roles.append(admin_role)
            
            db.session.add(admin_user)
            db.session.commit()
            
            flash(f'Organization "{org_name}" created successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating organization: {e}")
            flash('An error occurred while creating your organization. Please try again.', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for logged-in user"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'warning')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'warning')
            return render_template('auth/change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Your password has been changed successfully!', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('auth/change_password.html')


def log_audit(user_id, org_id, action, entity_type, entity_id, description):
    """Helper function to log audit entries"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            organisation_id=org_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            new_value=description,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:255]
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error logging audit: {e}")
