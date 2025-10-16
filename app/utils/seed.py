"""
Seed database with initial data
"""

from app import db
from app.models import Organisation, Department, Role, Tag, User, SystemSettings, EmailTemplate
from datetime import datetime


def seed_database():
    """Seed database with initial data"""
    print("Starting database seeding...")
    
    # Create default roles
    roles_data = [
        {'name': 'Admin', 'description': 'Full system access', 'permissions': '{"all": true}'},
        {'name': 'Manager', 'description': 'Manage team and tasks', 'permissions': '{"manage_tasks": true, "manage_team": true}'},
        {'name': 'Employee', 'description': 'Basic user access', 'permissions': '{"view_tasks": true, "update_own_tasks": true}'},
    ]
    
    for role_data in roles_data:
        if not Role.query.filter_by(name=role_data['name']).first():
            role = Role(**role_data)
            db.session.add(role)
            print(f"✓ Created role: {role_data['name']}")
    
    db.session.commit()
    
    # Create default tags
    tags_data = [
        {'name': 'CEO', 'color': '#e74c3c'},
        {'name': 'Manager', 'color': '#3498db'},
        {'name': 'Developer', 'color': '#2ecc71'},
        {'name': 'Designer', 'color': '#9b59b6'},
        {'name': 'Marketing', 'color': '#f39c12'},
        {'name': 'Sales', 'color': '#1abc9c'},
        {'name': 'Co-founder', 'color': '#e67e22'},
    ]
    
    for tag_data in tags_data:
        if not Tag.query.filter_by(name=tag_data['name']).first():
            tag = Tag(**tag_data)
            db.session.add(tag)
            print(f"✓ Created tag: {tag_data['name']}")
    
    db.session.commit()
    
    # Create demo organisation
    demo_org = Organisation.query.filter_by(email='demo@flowdeck.org').first()
    if not demo_org:
        demo_org = Organisation(
            name='Demo Organisation',
            email='demo@flowdeck.org',
            contact='+1234567890',
            color_palette='#3498db',
            theme='light'
        )
        db.session.add(demo_org)
        db.session.commit()
        print(f"✓ Created demo organisation")
    
    # Create demo departments
    departments_data = [
        {'name': 'Engineering', 'description': 'Software development team'},
        {'name': 'Design', 'description': 'UI/UX design team'},
        {'name': 'Marketing', 'description': 'Marketing and growth team'},
        {'name': 'Sales', 'description': 'Sales and business development'},
    ]
    
    for dept_data in departments_data:
        if not Department.query.filter_by(name=dept_data['name'], organisation_id=demo_org.id).first():
            dept = Department(
                name=dept_data['name'],
                description=dept_data['description'],
                organisation_id=demo_org.id
            )
            db.session.add(dept)
            print(f"✓ Created department: {dept_data['name']}")
    
    db.session.commit()
    
    # Create demo admin user
    admin_role = Role.query.filter_by(name='Admin').first()
    admin_user = User.query.filter_by(email='admin@flowdeck.org').first()
    
    if not admin_user:
        engineering_dept = Department.query.filter_by(name='Engineering', organisation_id=demo_org.id).first()
        
        admin_user = User(
            name='Admin User',
            email='admin@flowdeck.org',
            phone='+1234567890',
            designation='System Administrator',
            organisation_id=demo_org.id,
            department_id=engineering_dept.id if engineering_dept else None,
            is_active=True,
            is_email_verified=True
        )
        admin_user.set_password('admin123')  # Change in production!
        admin_user.roles.append(admin_role)
        
        db.session.add(admin_user)
        db.session.commit()
        print(f"✓ Created admin user: admin@flowdeck.org (password: admin123)")
    
    # Create email templates
    templates_data = [
        {
            'name': 'welcome_email',
            'subject': 'Welcome to FlowDeck!',
            'body_html': '<h1>Welcome {{user_name}}!</h1><p>Your credentials: {{email}} / {{password}}</p>',
            'body_text': 'Welcome {{user_name}}! Your credentials: {{email}} / {{password}}',
            'variables': '["user_name", "email", "password", "verification_url"]',
            'description': 'Welcome email sent to new users'
        },
        {
            'name': 'task_assigned',
            'subject': 'New Task Assigned: {{task_title}}',
            'body_html': '<h2>New Task</h2><p>You have been assigned: {{task_title}}</p>',
            'body_text': 'New Task: You have been assigned: {{task_title}}',
            'variables': '["user_name", "task_title", "task_url", "priority", "due_date"]',
            'description': 'Email sent when task is assigned'
        },
        {
            'name': 'task_reminder',
            'subject': 'Task Reminder: {{task_title}}',
            'body_html': '<h2>Reminder</h2><p>Your task {{task_title}} is due soon!</p>',
            'body_text': 'Reminder: Your task {{task_title}} is due soon!',
            'variables': '["user_name", "task_title", "task_url", "due_date"]',
            'description': 'Reminder email for upcoming deadlines'
        }
    ]
    
    for template_data in templates_data:
        if not EmailTemplate.query.filter_by(name=template_data['name']).first():
            template = EmailTemplate(**template_data)
            db.session.add(template)
            print(f"✓ Created email template: {template_data['name']}")
    
    db.session.commit()
    
    # Create system settings
    settings_data = [
        {
            'setting_key': 'app_version',
            'setting_value': '1.0.0',
            'setting_type': 'string',
            'description': 'Application version',
            'is_public': True
        },
        {
            'setting_key': 'maintenance_mode',
            'setting_value': 'false',
            'setting_type': 'bool',
            'description': 'Enable maintenance mode',
            'is_public': False
        },
        {
            'setting_key': 'max_file_upload_size',
            'setting_value': '16777216',
            'setting_type': 'int',
            'description': 'Max file upload size in bytes',
            'is_public': False
        }
    ]
    
    for setting_data in settings_data:
        if not SystemSettings.query.filter_by(setting_key=setting_data['setting_key']).first():
            setting = SystemSettings(**setting_data)
            db.session.add(setting)
            print(f"✓ Created system setting: {setting_data['setting_key']}")
    
    db.session.commit()
    
    print("\n✅ Database seeding completed!")
    print("\n📝 Demo Login Credentials:")
    print("   Email: admin@flowdeck.org")
    print("   Password: admin123")
    print("\n⚠️  Remember to change the default password in production!")


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()
