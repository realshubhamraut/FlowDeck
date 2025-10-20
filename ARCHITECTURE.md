# FlowDeck - System Architecture

This document provides a comprehensive overview of FlowDeck's system architecture, components, and data flow.

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Browser    │  │    Mobile    │  │   Desktop    │         │
│  │   (HTML/CSS/ │  │   (Future    │  │   (Future    │         │
│  │   JavaScript)│  │    PWA)      │  │   Electron)  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                    HTTP/WebSocket
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────┐         │
│  │          Jinja2 Template Engine                    │         │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │         │
│  │  │   Base   │  │ Dashboard│  │   Task   │        │         │
│  │  │ Template │  │ Templates│  │ Templates│ ...    │         │
│  │  └──────────┘  └──────────┘  └──────────┘        │         │
│  └────────────────────────────────────────────────────┘         │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────┐         │
│  │           Flask Application Factory                │         │
│  │              (app/__init__.py)                     │         │
│  └───────────────────┬────────────────────────────────┘         │
│                      │                                          │
│  ┌───────────────────┼────────────────────────────────┐        │
│  │              BLUEPRINTS (Routes)                   │        │
│  │  ┌──────────┬────┴──────┬──────────┬──────────┐   │        │
│  │  │   Auth   │   Main    │  Admin   │   User   │   │        │
│  │  │  (7 rts) │  (5 rts)  │ (12 rts) │  (6 rts) │   │        │
│  │  └──────────┴───────────┴──────────┴──────────┘   │        │
│  │  ┌──────────┬────────────┬──────────┬─────────┐   │        │
│  │  │  Tasks   │    Chat    │Dashboard │   API   │   │        │
│  │  │ (10 rts) │   (6 rts)  │  (6 rts) │ (9 eps) │   │        │
│  │  └──────────┴────────────┴──────────┴─────────┘   │        │
│  └──────────────────────────────────────────────────┘          │
│                      │                                          │
│  ┌───────────────────┼────────────────────────────────┐        │
│  │           SOCKET.IO HANDLERS                       │        │
│  │  ┌────────────────┴────────────────┐               │        │
│  │  │  Chat Events  │ Notification    │               │        │
│  │  │   (9 events)  │ Events (3 evts) │               │        │
│  │  └───────────────┴─────────────────┘               │        │
│  └──────────────────────────────────────────────────┘          │
│                      │                                          │
└──────────────────────┼───────────────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
│                      │                                           │
│  ┌───────────────────┼────────────────────────────────┐         │
│  │              UTILITIES                             │         │
│  │  ┌────────────────┴────────────────┐               │         │
│  │  │  Email Utils   │   AI Utils     │               │         │
│  │  │  (5 functions) │ (4 functions)  │               │         │
│  │  └────────────────┬─────────────────┘              │         │
│  │                   │  Seed Utils                    │         │
│  │                   │  (1 function)                  │         │
│  └──────────────────────────────────────────────────┘           │
│                      │                                           │
└──────────────────────┼──────────────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────────────┐
│                    DATA LAYER                                    │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────┐         │
│  │            SQLAlchemy ORM                          │         │
│  │  ┌──────────┬──────────┬──────────┬──────────┐    │         │
│  │  │   User   │   Task   │Messaging │Analytics │    │         │
│  │  │  Models  │  Models  │  Models  │  Models  │    │         │
│  │  │ (5 tbls) │ (5 tbls) │ (5 tbls) │ (6 tbls) │    │         │
│  │  └──────────┴──────────┴──────────┴──────────┘    │         │
│  └───────────────────────────────────────────────────┘          │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────┐         │
│  │         DATABASE FEATURES                          │         │
│  │  ┌─────────────┬─────────────┬──────────────┐     │         │
│  │  │  Triggers   │    Views    │   Indexes    │     │         │
│  │  │ (5 triggers)│  (4 views)  │ (11 indexes) │     │         │
│  │  └─────────────┴─────────────┴──────────────┘     │         │
│  └───────────────────────────────────────────────────┘          │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────┐         │
│  │            SQLite Database                         │         │
│  │               (flowdeck.db)                        │         │
│  │          18 Tables + 4 Views                       │         │
│  └───────────────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   OpenAI     │  │  SMTP Server │  │  Google Cal  │          │
│  │   API        │  │  (Gmail)     │  │  API (Future)│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow Diagrams

### 1. User Authentication Flow

```
┌─────────┐
│ Browser │
└────┬────┘
     │
     │ 1. POST /auth/login
     │    {email, password}
     ▼
┌─────────────┐
│ Auth        │
│ Blueprint   │
└──────┬──────┘
       │
       │ 2. Verify credentials
       ▼
┌─────────────┐
│ User Model  │
│ (check      │
│  password)  │
└──────┬──────┘
       │
       │ 3. Create session
       ▼
┌─────────────┐
│ Flask-Login │
│ (login_user)│
└──────┬──────┘
       │
       │ 4. Log audit event
       ▼
┌─────────────┐
│ AuditLog    │
│ Model       │
└──────┬──────┘
       │
       │ 5. Redirect to dashboard
       ▼
┌─────────────┐
│ Dashboard   │
│ Blueprint   │
└─────────────┘
```

### 2. Real-time Chat Message Flow

```
┌─────────┐                    ┌─────────────┐
│ User A  │                    │  User B     │
│ Browser │                    │  Browser    │
└────┬────┘                    └──────▲──────┘
     │                                │
     │ 1. Send message via Socket.IO  │
     │    {content, channel_id}       │
     ▼                                │
┌─────────────┐                       │
│ Socket.IO   │                       │
│ Server      │                       │
└──────┬──────┘                       │
       │                              │
       │ 2. Save to database          │
       ▼                              │
┌─────────────┐                       │
│ Message     │                       │
│ Model       │                       │
└──────┬──────┘                       │
       │                              │
       │ 3. Get channel members       │
       ▼                              │
┌─────────────┐                       │
│ ChatChannel │                       │
│ Model       │                       │
└──────┬──────┘                       │
       │                              │
       │ 4. Emit to room              │
       │                              │
       └──────────────────────────────┘
              5. Real-time update
```

### 3. Task Creation and Notification Flow

```
┌─────────┐
│ Manager │
│ Browser │
└────┬────┘
     │
     │ 1. POST /tasks/create
     │    {title, assignees[], due_date}
     ▼
┌─────────────┐
│ Tasks       │
│ Blueprint   │
└──────┬──────┘
       │
       │ 2. Create task
       ▼
┌─────────────┐
│ Task Model  │
└──────┬──────┘
       │
       │ 3. Database trigger fires
       ▼
┌─────────────┐
│ Trigger:    │
│ notify_task │
│ _assignment │
└──────┬──────┘
       │
       │ 4. Create notifications
       ▼
┌─────────────┐
│ Notification│
│ Model       │
└──────┬──────┘
       │
       ├─────────────┬──────────────┐
       │             │              │
       ▼             ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Socket.IO│  │  Email   │  │ Task     │
│ Push     │  │  Async   │  │ History  │
│ Notif    │  │  Send    │  │ Log      │
└──────────┘  └──────────┘  └──────────┘
```

---

## 📊 Database Entity Relationship Diagram

```
┌────────────────┐
│  Organisation  │
│  ─────────────│
│  id            │◄────┐
│  name          │     │
│  logo          │     │
└────────────────┘     │
                       │
                       │
┌────────────────┐     │       ┌────────────────┐
│   Department   │     │       │      Role      │
│  ─────────────│     │       │  ─────────────│
│  id            │     │       │  id            │
│  name          │     │       │  name          │
│  organisation──┼─────┘       │  permissions   │
└────────┬───────┘             └───────┬────────┘
         │                             │
         │                             │
         │       ┌────────────────┐    │
         │       │      User      │    │
         │       │  ─────────────│    │
         └──────►│  id            │◄───┤
                 │  username      │    │
                 │  email         │    │
                 │  password_hash │    │
                 │  department_id │    │
                 │  organisation──┼────┘
                 └────────┬───────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    Task     │  │   Message   │  │Notification │
│ ───────────│  │ ───────────│  │ ───────────│
│ id          │  │ id          │  │ id          │
│ title       │  │ content     │  │ title       │
│ creator_id──┼──┤ sender_id───┼──┤ user_id─────┤
│ assignees[] │  │ channel_id  │  │ message     │
│ priority    │  │ read_by[]   │  │ is_read     │
│ status      │  └─────────────┘  └─────────────┘
│ due_date    │
└─────┬───────┘
      │
      ├──────────────┬──────────────┬──────────────┐
      │              │              │              │
      ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│TaskCommen│  │TaskAttac │  │ TimeLog  │  │  Task    │
│    t     │  │   hment  │  │          │  │ History  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

---

## 🔌 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND                             │
│                                                         │
│  ┌──────────────┐        ┌──────────────┐             │
│  │ HTTP Requests│        │  WebSocket   │             │
│  │  (REST API)  │        │  (Socket.IO) │             │
│  └──────┬───────┘        └──────┬───────┘             │
│         │                       │                      │
└─────────┼───────────────────────┼──────────────────────┘
          │                       │
          │                       │
┌─────────┼───────────────────────┼──────────────────────┐
│  FLASK  │  APPLICATION          │                      │
│         │                       │                      │
│  ┌──────▼─────────┐      ┌──────▼──────────┐          │
│  │   Blueprints   │      │  Socket.IO      │          │
│  │   (Routes)     │      │  Handlers       │          │
│  └──────┬─────────┘      └──────┬──────────┘          │
│         │                       │                      │
│         │  ┌────────────────────┼──────────┐           │
│         │  │    Middleware      │          │           │
│         ├──┤  • Flask-Login     │          │           │
│         │  │  • CSRF Protection │          │           │
│         │  │  • Session Mgmt    │          │           │
│         │  └────────────────────┘          │           │
│         │                                  │           │
│  ┌──────▼──────────────────────────────────▼────┐      │
│  │           SQLAlchemy ORM                     │      │
│  └──────┬───────────────────────────────────────┘      │
│         │                                              │
└─────────┼──────────────────────────────────────────────┘
          │
          │
┌─────────▼──────────────────────────────────────────────┐
│                    DATABASE                            │
│                                                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐      │
│  │  Tables    │  │  Triggers  │  │   Views    │      │
│  │ (18 total) │  │ (5 total)  │  │ (4 total)  │      │
│  └────────────┘  └────────────┘  └────────────┘      │
│                                                        │
│             SQLite (flowdeck.db)                       │
└────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                EXTERNAL SERVICES                        │
│                                                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │  OpenAI    │  │   SMTP     │  │  Google    │       │
│  │   API      │  │  Server    │  │  Calendar  │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│        ▲              ▲                ▲               │
│        │              │                │               │
└────────┼──────────────┼────────────────┼───────────────┘
         │              │                │
         │              │                │
    ┌────┴──────────────┴────────────────┴────┐
    │         Utility Modules                 │
    │  • AI Utils (OpenAI integration)        │
    │  • Email Utils (async sending)          │
    │  • Calendar Utils (future)              │
    └─────────────────────────────────────────┘
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   SECURITY LAYERS                       │
│                                                         │
│  ┌──────────────────────────────────────────────┐      │
│  │  Layer 1: Transport Security                │      │
│  │  • HTTPS (Production)                        │      │
│  │  • Secure cookies                            │      │
│  │  • CORS configuration                        │      │
│  └──────────────────────────────────────────────┘      │
│                       │                                │
│  ┌──────────────────────────────────────────────┐      │
│  │  Layer 2: Authentication                     │      │
│  │  • Flask-Login session management            │      │
│  │  • Password hashing (Werkzeug)               │      │
│  │  • Email verification tokens                 │      │
│  │  • Password reset tokens                     │      │
│  └──────────────────────────────────────────────┘      │
│                       │                                │
│  ┌──────────────────────────────────────────────┐      │
│  │  Layer 3: Authorization                      │      │
│  │  • Role-Based Access Control (RBAC)          │      │
│  │  • Permission decorators                     │      │
│  │    - @login_required                         │      │
│  │    - @admin_required                         │      │
│  │    - @manager_required                       │      │
│  └──────────────────────────────────────────────┘      │
│                       │                                │
│  ┌──────────────────────────────────────────────┐      │
│  │  Layer 4: Data Protection                    │      │
│  │  • SQL injection prevention (SQLAlchemy)     │      │
│  │  • XSS protection (Jinja2 auto-escape)       │      │
│  │  • CSRF tokens (Flask-WTF ready)             │      │
│  │  • Secure file uploads                       │      │
│  └──────────────────────────────────────────────┘      │
│                       │                                │
│  ┌──────────────────────────────────────────────┐      │
│  │  Layer 5: Audit & Monitoring                 │      │
│  │  • Audit logs for critical actions           │      │
│  │  • User activity tracking                    │      │
│  │  • Error logging                             │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
FlowDeck/
│
├── app/                          # Application package
│   ├── __init__.py               # Application factory
│   │
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── user.py               # User, Org, Dept, Role, Tag
│   │   ├── task.py               # Task, Comment, Attachment
│   │   ├── messaging.py          # Message, Channel, Notification
│   │   └── analytics.py          # Reports, Holidays, Leaves
│   │
│   ├── routes/                   # Blueprints (Controllers)
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication routes
│   │   ├── main.py               # Public routes
│   │   ├── admin.py              # Admin panel routes
│   │   ├── user.py               # User profile routes
│   │   ├── tasks.py              # Task management routes
│   │   ├── chat.py               # Chat routes
│   │   ├── dashboard.py          # Dashboard routes
│   │   └── api.py                # REST API endpoints
│   │
│   ├── sockets/                  # Socket.IO handlers
│   │   ├── __init__.py
│   │   ├── chat_events.py        # Chat event handlers
│   │   └── notification_events.py # Notification handlers
│   │
│   ├── utils/                    # Utility modules
│   │   ├── email.py              # Email functions
│   │   ├── ai.py                 # AI integration
│   │   └── seed.py               # Database seeding
│   │
│   ├── database/                 # Database features
│   │   └── __init__.py           # Triggers, views, indexes
│   │
│   ├── templates/                # Jinja2 templates
│   │   ├── base.html             # Base template
│   │   ├── main/                 # Public pages
│   │   │   └── landing.html
│   │   ├── auth/                 # Authentication pages
│   │   │   └── login.html
│   │   ├── dashboard/            # Dashboard pages
│   │   │   ├── index.html        # ✨ Main dashboard
│   │   │   ├── analytics.html    # ✨ Analytics
│   │   │   ├── calendar.html     # ✨ Calendar
│   │   │   └── notifications.html # ✨ Notifications
│   │   ├── tasks/                # Task pages (to be created)
│   │   ├── chat/                 # Chat pages (to be created)
│   │   ├── admin/                # Admin pages (to be created)
│   │   ├── user/                 # User pages (to be created)
│   │   └── errors/               # Error pages
│   │       ├── 404.html
│   │       ├── 500.html
│   │       └── 403.html
│   │
│   └── static/                   # Static files
│       ├── css/
│       │   └── main.css          # Main stylesheet
│       ├── js/                   # JavaScript files
│       └── uploads/              # User uploads
│
├── migrations/                   # Database migrations (Flask-Migrate)
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
├── setup.sh                      # Linux/macOS setup script
├── setup.bat                     # Windows setup script
├── README.md                     # Main documentation
├── QUICKSTART.md                 # Quick start guide
└── PROJECT_STATUS.md             # This file
```

---

## 🔄 Data Flow Patterns

### Pattern 1: CRUD Operations

```
Request → Route → Model → Database → Model → Route → Template → Response
```

**Example: View Task**
```
GET /tasks/123 
  → tasks.view_task(123)
    → Task.query.get(123)
      → SQLite SELECT
        → Task object
          → render_template('tasks/view.html', task=task)
            → HTML Response
```

### Pattern 2: Real-time Updates

```
Socket Event → Handler → Database → Broadcast → Clients
```

**Example: Send Message**
```
Socket: 'send_message' {content, channel_id}
  → chat_events.handle_send_message()
    → Message.create(content, channel_id)
      → SQLite INSERT
        → emit('new_message', room=channel_id)
          → All clients in room receive update
```

### Pattern 3: Background Jobs

```
Request → Route → Queue → Background Worker → Database → External Service
```

**Example: Send Email**
```
POST /tasks/create
  → tasks.create_task()
    → Task.create()
      → send_task_assignment_email() [async]
        → Thread starts
          → Email sent via SMTP
```

---

## 🚀 Deployment Architecture (Production)

```
┌──────────────────────────────────────────────────────────┐
│                     INTERNET                             │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│                   LOAD BALANCER                          │
│              (Nginx / AWS ALB / Azure LB)                │
└──────────┬──────────────────────┬────────────────────────┘
           │                      │
           ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│  Web Server 1   │    │  Web Server 2   │
│  ─────────────  │    │  ─────────────  │
│  Nginx          │    │  Nginx          │
│  (Reverse Proxy)│    │  (Reverse Proxy)│
└────────┬────────┘    └────────┬────────┘
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│ App Server 1    │    │ App Server 2    │
│ ───────────────│    │ ───────────────│
│ Gunicorn        │    │ Gunicorn        │
│ + Flask App     │    │ + Flask App     │
│ (3 workers)     │    │ (3 workers)     │
└────────┬────────┘    └────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
         ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│PostgreSQL│ │  Redis   │ │  File    │
│ Database │ │ (Sessions│ │ Storage  │
│          │ │  + Cache)│ │ (S3/Blob)│
└──────────┘ └──────────┘ └──────────┘
```

---

## 📈 Scalability Considerations

### Horizontal Scaling
- Multiple application servers behind load balancer
- Stateless application design (sessions in Redis)
- File uploads to object storage (S3/Azure Blob)

### Database Scaling
- Read replicas for analytics queries
- Connection pooling
- Query optimization with indexes

### Caching Strategy
- Redis for session storage
- Redis for Socket.IO pub/sub
- Browser caching for static assets
- CDN for static files

### Background Jobs
- Celery for asynchronous tasks
- Email sending queue
- Report generation queue
- Notification processing queue

---

## 🔧 Technology Integration Points

```
┌─────────────────────────────────────────────────────────┐
│                  FLASK APPLICATION                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Flask Extensions                               │   │
│  │  • Flask-SQLAlchemy → Database ORM              │   │
│  │  • Flask-Login → User session management        │   │
│  │  • Flask-Mail → Email sending                   │   │
│  │  • Flask-SocketIO → Real-time communication     │   │
│  │  • Flask-Migrate → Database migrations          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  External APIs                                  │   │
│  │  • OpenAI API → AI task generation              │   │
│  │  • Google Calendar API → Calendar sync (future) │   │
│  │  • SMTP Server → Email delivery                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Frontend Libraries (CDN)                       │   │
│  │  • Bootstrap 5.3.2 → UI framework               │   │
│  │  • Font Awesome 6.4.2 → Icons                   │   │
│  │  • Chart.js 4.4.0 → Charts                      │   │
│  │  • FullCalendar 6.1.9 → Calendar                │   │
│  │  • Socket.IO Client → Real-time                 │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

This architecture document provides a complete overview of FlowDeck's system design, data flow, and component interactions. All components shown as ✅ are fully implemented and operational.
