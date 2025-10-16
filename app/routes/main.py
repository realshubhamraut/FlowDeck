"""
Main Blueprint - Landing page and public routes
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('main/landing.html')


@bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')


@bp.route('/features')
def features():
    """Features page"""
    return render_template('main/features.html')


@bp.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('main/pricing.html')


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # TODO: Send email notification to admin
        # For now, just show success message
        flash(f'Thank you for contacting us, {name}! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('main/contact.html')
