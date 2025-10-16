"""
Email utility functions
"""

from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Error sending email: {e}")


def send_email(subject, recipients, text_body, html_body, sender=None):
    """Send email"""
    if not sender:
        sender = current_app.config['MAIL_DEFAULT_SENDER']
    
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Send asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_welcome_email(user, password, verification_token):
    """Send welcome email with login credentials"""
    verification_url = f"{current_app.config['APP_URL']}/auth/verify-email/{verification_token}"
    
    subject = f"Welcome to {current_app.config['APP_NAME']}!"
    
    text_body = f"""
    Welcome to {current_app.config['APP_NAME']}, {user.name}!
    
    Your account has been created. Here are your login credentials:
    
    Email: {user.email}
    Password: {password}
    
    Please verify your email by clicking the link below:
    {verification_url}
    
    For security reasons, we recommend changing your password after your first login.
    
    Login at: {current_app.config['APP_URL']}/auth/login
    
    Best regards,
    The {current_app.config['APP_NAME']} Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #3498db;">Welcome to {current_app.config['APP_NAME']}!</h2>
                <p>Hello {user.name},</p>
                <p>Your account has been created successfully. Here are your login credentials:</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>Password:</strong> <code style="background-color: #fff; padding: 2px 6px; border-radius: 3px;">{password}</code></p>
                </div>
                <p>Please verify your email by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email</a>
                </div>
                <p><small>For security reasons, we recommend changing your password after your first login.</small></p>
                <p><a href="{current_app.config['APP_URL']}/auth/login">Click here to login</a></p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #777; font-size: 12px;">
                    Best regards,<br>
                    The {current_app.config['APP_NAME']} Team
                </p>
            </div>
        </body>
    </html>
    """
    
    send_email(subject, [user.email], text_body, html_body)


def send_password_reset_email(user, reset_token):
    """Send password reset email"""
    reset_url = f"{current_app.config['APP_URL']}/auth/reset-password/{reset_token}"
    
    subject = "Password Reset Request"
    
    text_body = f"""
    Hello {user.name},
    
    We received a request to reset your password. Click the link below to reset it:
    {reset_url}
    
    If you didn't request a password reset, please ignore this email.
    
    This link will expire in 24 hours.
    
    Best regards,
    The {current_app.config['APP_NAME']} Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #e74c3c;">Password Reset Request</h2>
                <p>Hello {user.name},</p>
                <p>We received a request to reset your password. Click the button below to proceed:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #e74c3c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                </div>
                <p><small>If you didn't request a password reset, please ignore this email.</small></p>
                <p><small>This link will expire in 24 hours.</small></p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #777; font-size: 12px;">
                    Best regards,<br>
                    The {current_app.config['APP_NAME']} Team
                </p>
            </div>
        </body>
    </html>
    """
    
    send_email(subject, [user.email], text_body, html_body)


def send_task_assigned_email(user, task):
    """Send email when task is assigned"""
    task_url = f"{current_app.config['APP_URL']}/tasks/{task.id}"
    
    subject = f"New Task Assigned: {task.title}"
    
    text_body = f"""
    Hello {user.name},
    
    You have been assigned a new task:
    
    Title: {task.title}
    Priority: {task.priority}
    Due Date: {task.due_date.strftime('%B %d, %Y') if task.due_date else 'Not set'}
    
    View task details: {task_url}
    
    Best regards,
    The {current_app.config['APP_NAME']} Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #3498db;">New Task Assigned</h2>
                <p>Hello {user.name},</p>
                <p>You have been assigned a new task:</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">{task.title}</h3>
                    <p><strong>Priority:</strong> <span style="color: {'#e74c3c' if task.priority == 'urgent' else '#f39c12' if task.priority == 'high' else '#3498db'};">{task.priority.upper()}</span></p>
                    <p><strong>Due Date:</strong> {task.due_date.strftime('%B %d, %Y at %I:%M %p') if task.due_date else 'Not set'}</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{task_url}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">View Task</a>
                </div>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #777; font-size: 12px;">
                    Best regards,<br>
                    The {current_app.config['APP_NAME']} Team
                </p>
            </div>
        </body>
    </html>
    """
    
    send_email(subject, [user.email], text_body, html_body)


def send_task_reminder_email(user, task):
    """Send reminder email for upcoming task deadline"""
    task_url = f"{current_app.config['APP_URL']}/tasks/{task.id}"
    
    subject = f"Reminder: Task Due Soon - {task.title}"
    
    text_body = f"""
    Hello {user.name},
    
    This is a reminder that your task is due soon:
    
    Title: {task.title}
    Due Date: {task.due_date.strftime('%B %d, %Y at %I:%M %p') if task.due_date else 'Not set'}
    Status: {task.status}
    
    View task: {task_url}
    
    Best regards,
    The {current_app.config['APP_NAME']} Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #f39c12;">⏰ Task Reminder</h2>
                <p>Hello {user.name},</p>
                <p>This is a reminder that your task is due soon:</p>
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #f39c12; margin: 20px 0;">
                    <h3 style="margin-top: 0;">{task.title}</h3>
                    <p><strong>Due Date:</strong> {task.due_date.strftime('%B %d, %Y at %I:%M %p') if task.due_date else 'Not set'}</p>
                    <p><strong>Status:</strong> {task.status}</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{task_url}" style="background-color: #f39c12; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">View Task</a>
                </div>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #777; font-size: 12px;">
                    Best regards,<br>
                    The {current_app.config['APP_NAME']} Team
                </p>
            </div>
        </body>
    </html>
    """
    
    send_email(subject, [user.email], text_body, html_body)
