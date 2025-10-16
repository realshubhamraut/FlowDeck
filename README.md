# FlowDeck

**A Complete Production-Level Organization Workflow Management System**

FlowDeck is a modern, scalable web application built with Flask and SQLite, designed for comprehensive organization workflow management, real-time communication, and productivity tracking.

---

## 🚀 Features

### 👑 Admin Panel
- **Organisation Management**: Create and customize organizations with logo, color themes, and settings
- **User Management**: Create users, assign roles (Admin/Manager/Employee), manage departments
- **RBAC**: Role-Based Access Control with granular permissions
- **Department Management**: Create teams with dedicated chat channels and Kanban boards
- **Analytics Dashboard**: Organization-wide insights, team efficiency, productivity metrics

### 👥 User Features
- **Personalized Dashboard**: Overview of tasks, notifications, messages, and analytics
- **Task Management**:
  - Kanban board (Trello-like drag-and-drop)
  - Calendar view with Google Calendar sync
  - AI-powered task card generation
  - Task priorities, deliverables, time tracking
  - Comments, attachments, and history
- **Real-time Chat**:
  - Direct messaging and group channels
  - Typing indicators and online/offline status
  - File sharing and emoji support
  - Send task cards in chat
- **Time Tracking**: Built-in timers and productivity reports
- **Leave Management**: Request and approve leaves
- **Notifications**: Real-time in-app and email notifications

### 🤖 AI Integration
- Smart task card generation from prompts
- Auto-prioritization based on context
- Meeting notes to action items extraction
- Text summarization

### 📊 Analytics & Reports
- Weekly/monthly productivity reports
- Department efficiency metrics
- User performance tracking
- Export to CSV/PDF

### 📅 Calendar & Holidays
- Integrated calendar with task due dates
- Indian Holidays API integration
- Leave request tracking

---

## 🛠️ Tech Stack

- **Backend**: Flask 3.0
  - Blueprints for modular architecture
  - Flask-SocketIO for real-time features
  - Flask-Login for authentication
  - Flask-Mail for email notifications
  - Flask-Migrate for database migrations

- **Database**: SQLite with advanced features
  - Normalized schema (3NF)
  - Triggers for automated actions
  - Views for complex queries
  - Indexes for performance
  - Support for migration to PostgreSQL/MySQL

- **Frontend**:
  - Bootstrap 5.3
  - Font Awesome icons
  - Socket.IO client
  - Vanilla JavaScript

- **Real-time**: Socket.IO for messaging and notifications

- **APIs**:
  - OpenAI for AI task generation
  - Google Calendar API
  - Indian Holidays API
  - SendGrid/Gmail for emails

---

## 📁 Project Structure

```
FlowDeck/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User, Organisation, Department, Role, Tag
│   │   ├── task.py              # Task, Comments, Attachments, TimeLog
│   │   ├── messaging.py         # Message, ChatChannel, Notification
│   │   └── analytics.py         # Analytics, Holidays, Leaves, AuditLog
│   ├── routes/                  # Blueprint routes
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication
│   │   ├── main.py              # Landing page
│   │   ├── admin.py             # Admin panel
│   │   ├── user.py              # User profile
│   │   ├── tasks.py             # Task management
│   │   ├── chat.py              # Messaging
│   │   ├── dashboard.py         # User dashboard
│   │   └── api.py               # REST API
│   ├── sockets/                 # Socket.IO events
│   │   ├── __init__.py
│   │   ├── chat_events.py       # Chat socket events
│   │   └── notification_events.py
│   ├── database/                # Database utilities
│   │   └── __init__.py          # Triggers, views, functions
│   ├── utils/                   # Utility functions
│   │   ├── email.py             # Email templates
│   │   ├── ai.py                # AI integration
│   │   └── seed.py              # Database seeding
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── main/
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── user/
│   │   ├── tasks/
│   │   ├── chat/
│   │   └── dashboard/
│   └── static/                  # Static files
│       ├── css/
│       ├── js/
│       └── uploads/
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd FlowDeck
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Step 5: Initialize Database
```bash
python run.py init-db
python run.py seed
```

### Step 6: Run Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

---

## 🔑 Default Login Credentials

After seeding the database:
- **Email**: admin@flowdeck.org
- **Password**: admin123

⚠️ **Change this password immediately in production!**

---

## 📝 Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///flowdeck.db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@flowdeck.org

# API Keys
OPENAI_API_KEY=your-openai-api-key
GOOGLE_CALENDAR_API_KEY=your-google-api-key
SENDGRID_API_KEY=your-sendgrid-api-key

# App Configuration
APP_NAME=FlowDeck
APP_URL=http://localhost:5000
```

---

## 🗄️ Database Schema

The database uses SQLite with a fully normalized schema (3NF):

### Core Tables
- `organisations` - Organisation details
- `departments` - Teams/departments
- `users` - User accounts
- `roles` - User roles (Admin, Manager, Employee)
- `tags` - User and task tags

### Task Management
- `tasks` - Task details
- `task_comments` - Task comments
- `task_attachments` - File attachments
- `task_assignees` - Task-user assignments (many-to-many)
- `time_logs` - Time tracking
- `task_history` - Audit trail

### Communication
- `messages` - Chat messages
- `chat_channels` - Group chat channels
- `channel_members` - Channel memberships
- `notifications` - User notifications
- `online_status` - Real-time online status

### Analytics & Admin
- `analytics_reports` - Generated reports
- `holidays` - Holiday calendar
- `leave_requests` - Leave management
- `audit_logs` - System audit trail
- `system_settings` - Configuration
- `email_templates` - Email templates

### Database Views
- `user_productivity_summary` - User performance metrics
- `department_efficiency` - Department statistics
- `task_overview` - Comprehensive task view
- `recent_activity` - Activity feed

---

## 🔧 CLI Commands

```bash
# Initialize database
python run.py init-db

# Seed database with demo data
python run.py seed

# Create a new admin user
python run.py create-admin
```

---

## 🌐 API Endpoints

### Public Endpoints
- `GET /` - Landing page
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Protected Endpoints (Require Authentication)
- `GET /dashboard` - User dashboard
- `GET /tasks` - List tasks
- `POST /tasks/create` - Create task
- `GET /chat` - Chat interface
- `POST /chat/send` - Send message
- `GET /api/v1/tasks` - Tasks API
- `GET /api/v1/notifications` - Notifications API

### Admin Endpoints (Require Admin Role)
- `GET /admin` - Admin dashboard
- `POST /admin/users/create` - Create user
- `GET /admin/analytics` - Organization analytics

---

## 🔐 Security Features

- Password hashing with Werkzeug
- CSRF protection
- Session management with Flask-Login
- Email verification
- Role-based access control (RBAC)
- Input sanitization
- Secure file uploads
- SQL injection prevention (SQLAlchemy ORM)

---

## 📱 Progressive Web App (PWA) Ready

FlowDeck is designed to be installable as a PWA with:
- Responsive design
- Offline capability (can be extended)
- Mobile-friendly interface
- Push notifications support

---

## 🚀 Deployment

### Production Checklist
1. Change `SECRET_KEY` and all default passwords
2. Set `FLASK_ENV=production`
3. Use production-grade database (PostgreSQL/MySQL)
4. Enable HTTPS
5. Configure email service (SendGrid recommended)
6. Set up reverse proxy (Nginx)
7. Use process manager (Gunicorn + Supervisor)
8. Enable logging and monitoring
9. Set up backups
10. Configure firewall

### Docker Deployment (Optional)
```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
```

### Cloud Platforms
- **AWS**: EC2, RDS, S3
- **Render**: Easy deployment
- **Railway**: Simple setup
- **Heroku**: Quick deployment

---

## 🧪 Testing

```bash
# Run tests (to be implemented)
pytest

# Run with coverage
pytest --cov=app
```

---

## 📊 Performance Optimization

- Database indexing on frequently queried fields
- Query optimization with SQLAlchemy
- Static file caching
- Lazy loading for relationships
- Pagination for large datasets
- Asynchronous email sending
- Socket.IO for real-time updates (no polling)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Developed by PROXIM

---

## 📞 Support

For issues, questions, or feature requests:
- Create an issue on GitHub
- Email: support@flowdeck.org

---

## 🎯 Roadmap

- [ ] Mobile applications (React Native)
- [ ] Advanced AI features
- [ ] Video conferencing integration
- [ ] Advanced reporting with charts
- [ ] Multi-language support
- [ ] Third-party integrations (Slack, Jira, etc.)
- [ ] Advanced file preview
- [ ] Custom workflows
- [ ] API rate limiting
- [ ] Comprehensive test suite

---

## 🙏 Acknowledgments

- Flask community
- Bootstrap team
- Font Awesome
- Socket.IO team
- OpenAI
- All open-source contributors

---

**FlowDeck** - Streamline Your Workflow 🚀
