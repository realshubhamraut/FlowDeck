"""
Seed database with comprehensive dummy data
"""

from app import db
from app.models import (
    Organisation, Department, Role, Tag, User, SystemSettings, EmailTemplate,
    Task, TaskComment, TaskAttachment, TaskHistory, TimeLog,
    Meeting, MeetingAgendaItem, MeetingNote, MeetingAttachment,
    Message, ChatChannel, Notification, OnlineStatus,
    AnalyticsReport, Holiday, LeaveRequest, AuditLog
)
from datetime import datetime, timedelta
import random
import json
from werkzeug.security import generate_password_hash


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
    
    # Create additional users
    print("\n--- Creating additional users ---")
    users_data = [
        {'name': 'John Smith', 'email': 'john.smith@flowdeck.org', 'designation': 'Senior Developer', 'dept': 'Engineering', 'role': 'Employee'},
        {'name': 'Sarah Johnson', 'email': 'sarah.j@flowdeck.org', 'designation': 'Product Manager', 'dept': 'Engineering', 'role': 'Manager'},
        {'name': 'Mike Chen', 'email': 'mike.chen@flowdeck.org', 'designation': 'UI/UX Designer', 'dept': 'Design', 'role': 'Employee'},
        {'name': 'Emily Davis', 'email': 'emily.d@flowdeck.org', 'designation': 'Lead Designer', 'dept': 'Design', 'role': 'Manager'},
        {'name': 'David Brown', 'email': 'david.b@flowdeck.org', 'designation': 'Marketing Manager', 'dept': 'Marketing', 'role': 'Manager'},
        {'name': 'Lisa Wilson', 'email': 'lisa.w@flowdeck.org', 'designation': 'Content Writer', 'dept': 'Marketing', 'role': 'Employee'},
        {'name': 'Tom Anderson', 'email': 'tom.a@flowdeck.org', 'designation': 'Sales Executive', 'dept': 'Sales', 'role': 'Employee'},
        {'name': 'Rachel Green', 'email': 'rachel.g@flowdeck.org', 'designation': 'Sales Manager', 'dept': 'Sales', 'role': 'Manager'},
        {'name': 'James Martinez', 'email': 'james.m@flowdeck.org', 'designation': 'Backend Developer', 'dept': 'Engineering', 'role': 'Employee'},
        {'name': 'Nina Patel', 'email': 'nina.p@flowdeck.org', 'designation': 'Frontend Developer', 'dept': 'Engineering', 'role': 'Employee'},
    ]
    
    created_users = [admin_user]
    for user_data in users_data:
        if not User.query.filter_by(email=user_data['email']).first():
            dept = Department.query.filter_by(name=user_data['dept'], organisation_id=demo_org.id).first()
            role = Role.query.filter_by(name=user_data['role']).first()
            
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                phone=f'+123456{random.randint(1000, 9999)}',
                designation=user_data['designation'],
                organisation_id=demo_org.id,
                department_id=dept.id if dept else None,
                is_active=True,
                is_email_verified=True,
                date_of_birth=datetime.now() - timedelta(days=random.randint(8000, 15000))
            )
            user.set_password('password123')
            if role:
                user.roles.append(role)
            
            db.session.add(user)
            created_users.append(user)
            print(f"✓ Created user: {user_data['name']}")
    
    db.session.commit()
    
    # Assign tags to users
    print("\n--- Assigning tags to users ---")
    ceo_tag = Tag.query.filter_by(name='CEO').first()
    manager_tag = Tag.query.filter_by(name='Manager').first()
    dev_tag = Tag.query.filter_by(name='Developer').first()
    designer_tag = Tag.query.filter_by(name='Designer').first()
    
    if admin_user and ceo_tag:
        admin_user.tags.append(ceo_tag)
    
    for user in created_users:
        if 'Manager' in user.designation and manager_tag and manager_tag not in user.tags:
            user.tags.append(manager_tag)
        if 'Developer' in user.designation and dev_tag and dev_tag not in user.tags:
            user.tags.append(dev_tag)
        if 'Designer' in user.designation and designer_tag and designer_tag not in user.tags:
            user.tags.append(designer_tag)
    
    db.session.commit()
    
    # Create tasks
    print("\n--- Creating tasks ---")
    tasks_data = [
        {'title': 'Implement user authentication', 'status': 'completed', 'priority': 'high', 'days_ago': 30},
        {'title': 'Design dashboard mockups', 'status': 'completed', 'priority': 'medium', 'days_ago': 25},
        {'title': 'Set up CI/CD pipeline', 'status': 'in_progress', 'priority': 'high', 'days_ago': 10},
        {'title': 'Write API documentation', 'status': 'in_progress', 'priority': 'medium', 'days_ago': 8},
        {'title': 'Implement meeting management', 'status': 'completed', 'priority': 'high', 'days_ago': 5},
        {'title': 'Create marketing campaign', 'status': 'pending', 'priority': 'low', 'days_ago': 3},
        {'title': 'Update user profile UI', 'status': 'in_progress', 'priority': 'medium', 'days_ago': 7},
        {'title': 'Fix notification bugs', 'status': 'pending', 'priority': 'critical', 'days_ago': 2},
        {'title': 'Prepare Q1 sales report', 'status': 'in_review', 'priority': 'high', 'days_ago': 1},
        {'title': 'Optimize database queries', 'status': 'pending', 'priority': 'medium', 'days_ago': 0},
        {'title': 'Implement dark mode', 'status': 'in_progress', 'priority': 'low', 'days_ago': 15},
        {'title': 'Conduct user testing', 'status': 'pending', 'priority': 'medium', 'days_ago': 5},
    ]
    
    created_tasks = []
    for task_data in tasks_data:
        task = Task(
            title=task_data['title'],
            description=f"Description for {task_data['title']}. This is a sample task with detailed requirements.",
            status=task_data['status'],
            priority=task_data['priority'],
            created_by=random.choice(created_users).id,
            organisation_id=demo_org.id,
            start_date=datetime.now() - timedelta(days=task_data['days_ago']),
            due_date=datetime.now() + timedelta(days=random.randint(5, 30)),
            estimated_hours=random.randint(8, 40)
        )
        db.session.add(task)
        created_tasks.append(task)
        print(f"✓ Created task: {task_data['title']}")
    
    db.session.commit()
    
    # Assign tasks to users
    print("\n--- Assigning tasks to users ---")
    for task in created_tasks:
        assignees = random.sample(created_users, random.randint(1, 3))
        for assignee in assignees:
            if assignee not in task.assignees:
                task.assignees.append(assignee)
        
        # Assign tags
        if random.choice([True, False]):
            tags_to_assign = random.sample(Tag.query.all(), random.randint(1, 2))
            for tag in tags_to_assign:
                if tag not in task.tags:
                    task.tags.append(tag)
    
    db.session.commit()
    
    # Add task comments
    print("\n--- Adding task comments ---")
    comments_texts = [
        "Looking good! Let me know if you need any help.",
        "I've completed the initial implementation. Ready for review.",
        "Can we schedule a meeting to discuss this?",
        "I have some questions about the requirements.",
        "Great work! Just a few minor suggestions.",
        "This is blocked by another task.",
        "Updated the code based on your feedback.",
        "I think we should reconsider the approach.",
    ]
    
    for task in created_tasks[:8]:
        for _ in range(random.randint(1, 4)):
            comment = TaskComment(
                task_id=task.id,
                user_id=random.choice(created_users).id,
                comment=random.choice(comments_texts),
                created_at=task.created_at + timedelta(days=random.randint(1, 5))
            )
            db.session.add(comment)
    
    db.session.commit()
    print(f"✓ Added task comments")
    
    # Add task history
    print("\n--- Adding task history ---")
    for task in created_tasks:
        history = TaskHistory(
            task_id=task.id,
            user_id=random.choice(created_users).id,
            action='created',
            field_changed='status',
            old_value=None,
            new_value='pending',
            timestamp=task.created_at
        )
        db.session.add(history)
        
        if task.status != 'pending':
            history2 = TaskHistory(
                task_id=task.id,
                user_id=random.choice(task.assignees).id if task.assignees else random.choice(created_users).id,
                action='updated',
                field_changed='status',
                old_value='pending',
                new_value=task.status,
                timestamp=task.created_at + timedelta(days=random.randint(1, 3))
            )
            db.session.add(history2)
    
    db.session.commit()
    print(f"✓ Added task history")
    
    # Add time logs
    print("\n--- Adding time logs ---")
    for task in created_tasks[:6]:
        for assignee in task.assignees:
            log = TimeLog(
                task_id=task.id,
                user_id=assignee.id,
                hours_logged=random.uniform(1.0, 8.0),
                description=f"Work done on {task.title}",
                log_date=task.created_at + timedelta(days=random.randint(1, 5))
            )
            db.session.add(log)
    
    db.session.commit()
    print(f"✓ Added time logs")
    
    # Create meetings
    print("\n--- Creating meetings ---")
    meetings_data = [
        {'title': 'Sprint Planning Meeting', 'type': 'planning', 'days_offset': -7, 'duration': 120},
        {'title': 'Daily Standup', 'type': 'standup', 'days_offset': -1, 'duration': 15},
        {'title': 'Client Presentation', 'type': 'client', 'days_offset': 3, 'duration': 60},
        {'title': 'Design Review', 'type': 'review', 'days_offset': 5, 'duration': 90},
        {'title': 'Team Retrospective', 'type': 'general', 'days_offset': -14, 'duration': 60},
        {'title': 'Product Roadmap Discussion', 'type': 'planning', 'days_offset': 7, 'duration': 120},
        {'title': 'One-on-One: Sarah & John', 'type': 'one-on-one', 'days_offset': 2, 'duration': 30},
        {'title': 'Marketing Strategy Session', 'type': 'general', 'days_offset': 10, 'duration': 90},
    ]
    
    created_meetings = []
    for meet_data in meetings_data:
        meeting_time = datetime.now() + timedelta(days=meet_data['days_offset'])
        meeting = Meeting(
            title=meet_data['title'],
            description=f"Detailed description for {meet_data['title']}",
            meeting_type=meet_data['type'],
            start_time=meeting_time,
            end_time=meeting_time + timedelta(minutes=meet_data['duration']),
            location='Conference Room A' if random.choice([True, False]) else 'https://meet.flowdeck.org/room123',
            organiser_id=random.choice(created_users[:4]).id,
            organisation_id=demo_org.id,
            priority='high' if meet_data['type'] == 'client' else 'medium',
            status='completed' if meet_data['days_offset'] < 0 else 'scheduled'
        )
        db.session.add(meeting)
        created_meetings.append(meeting)
        print(f"✓ Created meeting: {meet_data['title']}")
    
    db.session.commit()
    
    # Add meeting attendees
    print("\n--- Adding meeting attendees ---")
    for meeting in created_meetings:
        attendee_count = random.randint(2, 6)
        attendees = random.sample(created_users, attendee_count)
        
        for attendee in attendees:
            # Determine RSVP status
            if meeting.start_time < datetime.now():
                rsvp = random.choice(['accepted', 'accepted', 'declined'])
            else:
                rsvp = random.choice(['pending', 'accepted', 'tentative'])
            
            meeting.attendees_list.append(attendee)
            # Set RSVP in the association table
            db.session.execute(
                db.text("UPDATE meeting_attendees SET rsvp_status = :rsvp WHERE meeting_id = :mid AND user_id = :uid"),
                {'rsvp': rsvp, 'mid': meeting.id, 'uid': attendee.id}
            )
    
    db.session.commit()
    
    # Add meeting agenda items
    print("\n--- Adding meeting agenda items ---")
    agenda_items = [
        "Review previous action items",
        "Discuss project progress",
        "Address blockers and concerns",
        "Plan upcoming sprint",
        "Q&A session",
        "Present latest designs",
        "Budget discussion",
        "Team updates",
    ]
    
    for meeting in created_meetings[:5]:
        for i, agenda_text in enumerate(random.sample(agenda_items, random.randint(2, 4))):
            agenda = MeetingAgendaItem(
                meeting_id=meeting.id,
                title=agenda_text,
                duration_minutes=random.choice([10, 15, 20, 30]),
                order_index=i
            )
            db.session.add(agenda)
    
    db.session.commit()
    print(f"✓ Added meeting agenda items")
    
    # Add meeting notes for completed meetings
    print("\n--- Adding meeting notes ---")
    for meeting in created_meetings:
        if meeting.status == 'completed':
            note = MeetingNote(
                meeting_id=meeting.id,
                user_id=meeting.organiser_id,
                content=f"Meeting notes for {meeting.title}:\n\n- Discussed key points\n- Made several decisions\n- Assigned action items\n- All attendees participated actively",
                created_at=meeting.end_time + timedelta(minutes=30)
            )
            db.session.add(note)
    
    db.session.commit()
    print(f"✓ Added meeting notes")
    
    # Create chat channels
    print("\n--- Creating chat channels ---")
    channels_data = [
        {'name': 'general', 'description': 'General team discussions', 'type': 'public'},
        {'name': 'engineering', 'description': 'Engineering team channel', 'type': 'private'},
        {'name': 'design', 'description': 'Design team channel', 'type': 'private'},
        {'name': 'random', 'description': 'Random conversations', 'type': 'public'},
        {'name': 'project-alpha', 'description': 'Project Alpha discussions', 'type': 'private'},
    ]
    
    created_channels = []
    for channel_data in channels_data:
        channel = ChatChannel(
            name=channel_data['name'],
            description=channel_data['description'],
            channel_type=channel_data['type'],
            created_by=admin_user.id,
            organisation_id=demo_org.id
        )
        db.session.add(channel)
        created_channels.append(channel)
        print(f"✓ Created channel: {channel_data['name']}")
    
    db.session.commit()
    
    # Add channel members
    print("\n--- Adding channel members ---")
    for channel in created_channels:
        if channel.channel_type == 'public':
            members = created_users
        else:
            members = random.sample(created_users, random.randint(3, 7))
        
        for member in members:
            channel.members.append(member)
    
    db.session.commit()
    
    # Add messages
    print("\n--- Adding messages ---")
    message_texts = [
        "Hey team, how's everyone doing?",
        "Just pushed the latest changes to main branch",
        "Can someone review my PR?",
        "Meeting starts in 10 minutes!",
        "Great job on the last sprint!",
        "I'll be working from home today",
        "Does anyone have experience with this library?",
        "Let's discuss this in the next standup",
        "Thanks for the help!",
        "I've updated the documentation",
    ]
    
    for channel in created_channels:
        for _ in range(random.randint(5, 15)):
            message = Message(
                sender_id=random.choice(channel.members).id,
                channel_id=channel.id,
                content=random.choice(message_texts),
                message_type='text',
                created_at=datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23)),
                is_read=random.choice([True, True, False])
            )
            db.session.add(message)
    
    db.session.commit()
    print(f"✓ Added messages")
    
    # Create notifications
    print("\n--- Creating notifications ---")
    notification_types = [
        ('task_assigned', 'You have been assigned a new task'),
        ('task_updated', 'A task you are assigned to has been updated'),
        ('meeting_invited', 'You have been invited to a meeting'),
        ('message_received', 'You have a new message'),
        ('comment_added', 'Someone commented on your task'),
    ]
    
    for user in created_users[:8]:
        for _ in range(random.randint(2, 5)):
            notif_type, notif_text = random.choice(notification_types)
            notification = Notification(
                user_id=user.id,
                title=notif_type.replace('_', ' ').title(),
                message=notif_text,
                notification_type=notif_type,
                is_read=random.choice([True, False]),
                created_at=datetime.now() - timedelta(days=random.randint(0, 5))
            )
            db.session.add(notification)
    
    db.session.commit()
    print(f"✓ Added notifications")
    
    # Create holidays
    print("\n--- Creating holidays ---")
    holidays_data = [
        {'name': 'New Year', 'date': datetime(2024, 1, 1)},
        {'name': 'Independence Day', 'date': datetime(2024, 7, 4)},
        {'name': 'Christmas', 'date': datetime(2024, 12, 25)},
        {'name': 'Thanksgiving', 'date': datetime(2024, 11, 28)},
    ]
    
    for holiday_data in holidays_data:
        holiday = Holiday(
            name=holiday_data['name'],
            date=holiday_data['date'],
            organisation_id=demo_org.id,
            is_recurring=True
        )
        db.session.add(holiday)
        print(f"✓ Created holiday: {holiday_data['name']}")
    
    db.session.commit()
    
    # Create leave requests
    print("\n--- Creating leave requests ---")
    leave_types = ['sick_leave', 'casual_leave', 'annual_leave']
    leave_statuses = ['pending', 'approved', 'rejected']
    
    for user in created_users[:6]:
        leave = LeaveRequest(
            user_id=user.id,
            leave_type=random.choice(leave_types),
            start_date=datetime.now() + timedelta(days=random.randint(5, 30)),
            end_date=datetime.now() + timedelta(days=random.randint(31, 40)),
            reason="Personal reasons",
            status=random.choice(leave_statuses),
            organisation_id=demo_org.id
        )
        db.session.add(leave)
    
    db.session.commit()
    print(f"✓ Added leave requests")
    
    # Create analytics reports
    print("\n--- Creating analytics reports ---")
    report_types = ['tasks', 'users', 'meetings', 'productivity']
    
    for report_type in report_types:
        report = AnalyticsReport(
            title=f"{report_type.title()} Report - {datetime.now().strftime('%B %Y')}",
            report_type=report_type,
            generated_by=admin_user.id,
            organisation_id=demo_org.id,
            data_json=json.dumps({
                'total': random.randint(50, 200),
                'completed': random.randint(30, 100),
                'pending': random.randint(10, 50)
            }),
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        db.session.add(report)
        print(f"✓ Created report: {report.title}")
    
    db.session.commit()
    
    # Create audit logs
    print("\n--- Creating audit logs ---")
    actions = ['login', 'logout', 'create_task', 'update_task', 'delete_task', 'create_meeting']
    
    for user in created_users[:5]:
        for _ in range(random.randint(3, 8)):
            log = AuditLog(
                user_id=user.id,
                action=random.choice(actions),
                resource_type='task' if 'task' in random.choice(actions) else 'meeting',
                resource_id=random.randint(1, 10),
                organisation_id=demo_org.id,
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0",
                timestamp=datetime.now() - timedelta(days=random.randint(0, 7))
            )
            db.session.add(log)
    
    db.session.commit()
    print(f"✓ Added audit logs")
    
    # Set online status for some users
    print("\n--- Setting online status ---")
    for user in created_users[:5]:
        status = OnlineStatus(
            user_id=user.id,
            is_online=random.choice([True, False]),
            last_seen=datetime.now() - timedelta(minutes=random.randint(1, 120))
        )
        db.session.add(status)
    
    db.session.commit()
    print(f"✓ Set online status")
    
    print("\n" + "="*60)
    print("✅ Database seeding completed with comprehensive dummy data!")
    print("="*60)
    print("\n📊 Summary:")
    print(f"   - Users: {len(created_users)}")
    print(f"   - Tasks: {len(created_tasks)}")
    print(f"   - Meetings: {len(created_meetings)}")
    print(f"   - Chat Channels: {len(created_channels)}")
    print(f"   - Departments: 4")
    print(f"   - Roles: 3")
    print(f"   - Tags: 7")
    print("\n📝 Demo Login Credentials:")
    print("   Email: admin@flowdeck.org")
    print("   Password: admin123")
    print("\n   All other users:")
    print("   Password: password123")
    print("\n⚠️  Remember to change default passwords in production!")


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()
