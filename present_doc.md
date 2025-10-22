# Database Initialization, Connection, and Dynamic Updates

FlowDeck uses Flask-SQLAlchemy to manage database connections, initialization, and dynamic updates through Python code. 

## 1. Initialization & Connection
- **App Factory Pattern**: The database is initialized in `app/__init__.py` using Flask’s application factory.
- **SQLAlchemy Setup**: The `SQLAlchemy` object is instantiated and linked to the Flask app.
- **Migration Support**: `Flask-Migrate` is used for schema migrations and upgrades.
- **Configuration**: Database URI and settings are loaded from `.env` and passed to the app config.

**Files to refer:**
- [`app/__init__.py`](app/__init__.py) – App factory, SQLAlchemy and migration setup
- [`run.py`](run.py) – Entry point, triggers initialization
- [`app/database/__init__.py`](app/database/__init__.py) – Utility functions for DB operations

## 2. Model Definitions
- **ORM Models**: All tables are represented as Python classes in `app/models/` (e.g., `User`, `Task`, `Message`).
- **Relationships**: Foreign keys and relationships are defined using SQLAlchemy’s `db.relationship` and `db.ForeignKey`.
- **CRUD Methods**: Models often include helper methods for create, update, and delete operations.

**Files to refer:**
- [`app/models/user.py`](app/models/user.py) – User, Department, Role models
- [`app/models/task.py`](app/models/task.py) – Task, Assignee, Comment models
- [`app/models/messaging.py`](app/models/messaging.py) – Message, Channel models

## 3. Dynamic Updates & CRUD Operations
- **Routes & Blueprints**: CRUD actions are triggered by HTTP requests to Flask routes (e.g., `/tasks/create`, `/user/edit`).
- **Form Handling**: WTForms and Flask-WTF are used for form validation and submission.
- **Click Events**: User actions (button clicks, form submissions) in the frontend send requests to backend routes, which perform DB operations.
- **Variables Used**:
  - `db.session.add()` – Add new records
  - `db.session.commit()` – Save changes
  - `db.session.delete()` – Remove records
  - Query variables: `User.query`, `Task.query`, etc.
  - Form variables: `form.field.data` for input values
- **AJAX & Real-time**: Some updates (e.g., chat, notifications) use Socket.IO or AJAX for instant DB changes.

**Files to refer:**
- [`app/routes/tasks.py`](app/routes/tasks.py) – Task CRUD (create, edit, delete)
- [`app/routes/user.py`](app/routes/user.py) – User profile updates
- [`app/routes/chat.py`](app/routes/chat.py) – Message creation and updates
- [`app/routes/meetings.py`](app/routes/meetings.py) – Meeting CRUD
- [`app/routes/admin.py`](app/routes/admin.py) – Admin CRUD for users/departments

## 4. Example Workflow
- **Create Task**:
  1. User clicks “Create Task” → Form submitted to `/tasks/create`
  2. Backend validates form, instantiates `Task` object
  3. `db.session.add(task)` and `db.session.commit()` save to DB
  4. Redirect or AJAX response updates UI
- **Edit Profile**:
  1. User edits profile → Form submitted to `/user/edit`
  2. Backend fetches user, updates fields
  3. `db.session.commit()` saves changes
- **Delete Message**:
  1. User clicks delete on a message → AJAX request to `/chat/delete`
  2. Backend deletes message with `db.session.delete()`
  3. UI updates in real-time via Socket.IO

## 5. Real-time & Triggered Updates
- **Socket Events**: Chat, notifications, and online status are updated instantly via Socket.IO events, which also update the DB.
- **Triggers**: Some DB triggers (in SQL) automate updates (e.g., task completion, audit logs).

## 6. Error Handling & Transactions
- **Try/Except Blocks**: Used to catch DB errors and rollback transactions if needed.
- **Validation**: WTForms and custom validators ensure data integrity before DB operations.

---

**In summary:**
FlowDeck’s database is initialized and connected via Flask-SQLAlchemy, with models representing all entities. CRUD operations are triggered by user actions (clicks, form submissions) and handled in route files, using SQLAlchemy session methods. Real-time updates and triggers ensure the database stays in sync with user activity. For details, see the files above.

# Flask Implementation

FlowDeck uses Flask’s modular architecture to build a scalable, maintainable web application. The project leverages Flask’s features such as Blueprints, SocketIO, authentication, and configuration management.

## 1. Application Factory & Initialization
- The app is created using the application factory pattern for flexibility and testing.
- Configuration is loaded from environment variables and `.env` files.

**Files to refer:**
- [`app/__init__.py`](app/__init__.py) – Application factory, extension initialization
- [`run.py`](run.py) – Entry point for running the Flask app

## 2. Modular Blueprints
- Features are separated into Blueprints for maintainability (auth, admin, user, tasks, chat, dashboard, meetings, API).
- Each Blueprint has its own routes and templates.

**Files to refer:**
- [`app/routes/`](app/routes/) – All route files (e.g., `auth.py`, `admin.py`, `tasks.py`, `chat.py`, `dashboard.py`, `meetings.py`, `api.py`)
- [`app/templates/`](app/templates/) – Jinja2 templates for each module

## 3. Database Integration
- Uses Flask-SQLAlchemy for ORM and database management.
- Models are defined in the `app/models/` directory.
- Flask-Migrate is used for schema migrations.

**Files to refer:**
- [`app/models/`](app/models/) – All model files
- [`app/database/__init__.py`](app/database/__init__.py) – Database utilities
- [`instance/schema.sql`](instance/schema.sql) – Raw schema

## 4. Real-time Features
- Flask-SocketIO enables real-time messaging and notifications.
- Socket events are handled in the `app/sockets/` directory.

**Files to refer:**
- [`app/sockets/chat_events.py`](app/sockets/chat_events.py) – Chat socket events
- [`app/sockets/notification_events.py`](app/sockets/notification_events.py) – Notification socket events

## 5. Authentication & Security
- Flask-Login manages user sessions and authentication.
- CSRF protection via Flask-WTF.
- Password hashing with Werkzeug.

**Files to refer:**
- [`app/routes/auth.py`](app/routes/auth.py) – Login, registration, password management
- [`app/models/user.py`](app/models/user.py) – User model, password hashing
- [`app/utils/validators.py`](app/utils/validators.py) – Input validation

## 6. Email & Notifications
- Flask-Mail for email notifications.
- Utility functions for sending emails and notifications.

**Files to refer:**
- [`app/utils/email.py`](app/utils/email.py) – Email templates and sending
- [`app/routes/admin.py`](app/routes/admin.py) – Admin notifications

## 7. Configuration & Environment
- Uses `.env` files and `python-dotenv` for environment configuration.
- Sensitive settings (keys, passwords) are loaded securely.

**Files to refer:**
- [`.env.example`](.env.example) – Environment variable template
- [`run.py`](run.py) – Loads configuration

## 8. Static Files & Templates
- Static assets (CSS, JS, images) are served from `app/static/`.
- Jinja2 templates are organized by feature in `app/templates/`.

**Files to refer:**
- [`app/static/`](app/static/) – CSS, JS, images, uploads
- [`app/templates/`](app/templates/) – All HTML templates

---

**In summary:**  
FlowDeck’s Flask implementation is modular, secure, and scalable, using Blueprints, extensions, and best practices for web development. Review the files above for details on each component.

---

## Database Normalization

FlowDeck’s database schema is normalized to Third Normal Form (3NF) for data integrity, scalability, and minimal redundancy. Here’s how normalization is achieved, with direct file links:

### 1. Entity Separation (1NF)
- Each table represents a single entity (e.g., users, tasks, departments, roles, tags).
- All columns hold atomic values (no lists or nested data).
- **Files:**
  - [`app/models/user.py`](app/models/user.py) – User, Organisation, Department, Role, Tag models
  - [`app/models/task.py`](app/models/task.py) – Task, Comments, Attachments, TimeLog models
  - [`app/models/meeting.py`](app/models/meeting.py) – Meeting, Agenda, Notes, Attachments models
  - [`instance/schema.sql`](instance/schema.sql) – Full schema definition

### 2. Relationships & Foreign Keys (2NF)
- All non-key attributes are fully dependent on the primary key.
- Foreign keys link related tables (e.g., tasks.department_id → departments.id).
- **Files:**
  - [`app/models/task.py`](app/models/task.py) – Task has department_id, assignee_id, etc.
  - [`app/models/messaging.py`](app/models/messaging.py) – Message, ChatChannel, Notification models
  - [`instance/schema.sql`](instance/schema.sql) – Foreign key constraints

### 3. Elimination of Transitive Dependencies (3NF)
- No non-key attribute depends on another non-key attribute.
- Join tables are used for many-to-many relationships (e.g., task_assignees, user_roles, meeting_attendees).
- **Files:**
  - [`app/models/task.py`](app/models/task.py) – `task_assignees` for tasks ↔ users
  - [`app/models/user.py`](app/models/user.py) – `user_roles` for users ↔ roles
  - [`app/models/meeting.py`](app/models/meeting.py) – `meeting_attendees` for meetings ↔ users
  - [`instance/schema.sql`](instance/schema.sql) – Join table definitions

### 4. Modularization & Reusability
- Blueprints and models are modular, separating concerns and making relationships explicit.
- Utility tables (e.g., tags, roles, departments) are referenced via foreign keys, not duplicated.
- **Files:**
  - [`app/models/`](app/models/) – All model files
  - [`app/routes/`](app/routes/) – Blueprints for modular access
  - [`instance/schema.sql`](instance/schema.sql) – Table and relationship structure

### 5. Views & Triggers
- Database views (e.g., user_productivity_summary, department_efficiency) aggregate normalized data for reporting.
- Triggers automate updates and maintain integrity.
- **Files:**
  - [`app/database/__init__.py`](app/database/__init__.py) – Database utilities
  - [`instance/schema.sql`](instance/schema.sql) – View and trigger definitions

---

**In summary:**
Normalization in FlowDeck is achieved by separating entities, using foreign keys for relationships, join tables for many-to-many links, and eliminating transitive dependencies. The schema is modular, scalable, and maintains data integrity. Review the files above for implementation details.

---

# Database Schema

![er-diagrm](/schema.svg)

FlowDeck uses a fully normalized relational database schema (3NF) designed for scalability, integrity, and rich organizational features. Below is a concise summary of the schema and its key components:

## Core Entities
- **Organisations**: Stores organization details, logo, theme, and contact info.
- **Departments**: Teams within organizations, linked to users and tasks.
- **Users**: User accounts with profile, authentication, and leave quotas.
- **Roles**: RBAC roles (Admin, Manager, Employee) with permissions.
- **Tags**: Labels for users and tasks.

## Task Management
- **Tasks**: Core task records with status, priority, deadlines, and assignment.
- **Task Comments**: Threaded comments for collaboration.
- **Task Attachments**: File uploads linked to tasks.
- **Task Assignees**: Many-to-many user-task assignments.
- **Time Logs**: Tracks time spent on tasks.
- **Task History**: Audit trail of changes.
- **Task Tags**: Many-to-many tags for tasks.

## Communication
- **Messages**: Direct and channel chat messages, with attachments and task cards.
- **Chat Channels**: Group chat rooms, linked to departments and organizations.
- **Channel Members**: Many-to-many user-channel memberships.
- **Online Status**: Tracks user presence and socket connections.
- **Typing Indicators**: Real-time typing status in chat.
- **Notifications**: In-app alerts for tasks, messages, and system events.

## Meeting Management
- **Meetings**: Scheduled events with type, location, and organizer.
- **Meeting Attendees**: RSVP and status for users in meetings.
- **Meeting Agenda**: Structured agenda items with duration and order.
- **Meeting Notes**: Collaborative meeting notes.
- **Meeting Attachments**: Files linked to meetings.

## Analytics & Admin
- **Analytics Reports**: Generated reports for productivity and efficiency.
- **Holidays**: Holiday calendar for leave management.
- **Leave Requests**: Tracks user leave applications and approvals.
- **Audit Logs**: System-wide audit trail for compliance.
- **System Settings**: Configurable app settings per organization.
- **Email Templates**: Customizable email content for notifications.

## Views & Triggers
- **Views**:
  - `user_productivity_summary`: Aggregates user performance metrics.
  - `department_efficiency`: Department-level stats and completion rates.
  - `task_overview`: Comprehensive task details and status.
  - `recent_activity`: Latest actions (task creation/completion).
- **Triggers**:
  - Auto-update timestamps and completion dates.
  - Log user creation and task changes.
  - Update task hours on time log entry.
  - Notify users on task assignment.

## Relationships & Integrity
- Extensive use of foreign keys for referential integrity.
- Many-to-many relationships via join tables (e.g., `task_assignees`, `user_roles`, `channel_members`).
- Cascading deletes and updates for data consistency.
- Indexes on frequently queried fields for performance.

## Example Table Relationships
- **Users ↔ Departments ↔ Organisations**: Users belong to departments, which belong to organizations.
- **Tasks ↔ Departments ↔ Users**: Tasks are assigned to departments and users.
- **Messages ↔ Chat Channels ↔ Users**: Messages can be direct or in channels, linked to users.
- **Meetings ↔ Attendees ↔ Users**: Meetings have multiple attendees, each with RSVP status.

---

**In summary:**
FlowDeck’s schema supports advanced workflow, communication, analytics, and admin features, with robust normalization and integrity. For details, see [`instance/schema.sql`](instance/schema.sql).

---



# Socket.IO Implementation

FlowDeck uses Flask-SocketIO to enable real-time communication for chat, notifications, and live updates. The implementation is modular and integrated with Flask’s authentication and routing.

## 1. SocketIO Initialization
- Flask-SocketIO is initialized in the application factory.
- The SocketIO instance is attached to the Flask app and configured for async support.

**Files to refer:**
- [`app/__init__.py`](app/__init__.py) – SocketIO initialization and configuration

## 2. Event Handling Structure
- Socket events are organized in the `app/sockets/` directory for modularity.
- Separate files handle chat events and notification events.

**Files to refer:**
- [`app/sockets/chat_events.py`](app/sockets/chat_events.py) – Handles chat messages, typing indicators, user presence, channel events
- [`app/sockets/notification_events.py`](app/sockets/notification_events.py) – Handles real-time notifications, alerts, and updates

## 3. Integration with Blueprints and Models
- Socket events interact with Flask routes and database models for persistence and business logic.
- User authentication is checked for socket connections to ensure secure communication.

**Files to refer:**
- [`app/routes/chat.py`](app/routes/chat.py) – Chat routes, integration with socket events
- [`app/routes/dashboard.py`](app/routes/dashboard.py) – Dashboard updates via sockets
- [`app/models/messaging.py`](app/models/messaging.py) – Message and channel models

## 4. Real-time Features
- Direct messaging and group chat channels
- Typing indicators, online/offline status
- Real-time notifications for tasks, meetings, and system alerts
- Live updates for dashboards and activity feeds

**Files to refer:**
- [`app/sockets/`](app/sockets/) – All socket event files
- [`app/templates/chat/index.html`](app/templates/chat/index.html) – Frontend integration for chat
- [`app/templates/dashboard/index.html`](app/templates/dashboard/index.html) – Frontend integration for notifications

## 5. Frontend Integration
- Uses Socket.IO client in JavaScript to connect to the backend and handle events.
- Real-time UI updates for chat, notifications, and user status.

**Files to refer:**
- [`app/static/js/`](app/static/js/) – Socket.IO client scripts (if present)
- [`app/templates/chat/index.html`](app/templates/chat/index.html) – JS integration for chat
- [`app/templates/dashboard/index.html`](app/templates/dashboard/index.html) – JS integration for notifications

---

**In summary:**  
FlowDeck’s Socket.IO implementation provides robust real-time features for chat, notifications, and live updates, with modular event handling and secure integration with Flask’s authentication and models. Review the files above for details on each component.

---

# Frontend Implementation

FlowDeck’s frontend is designed for a modern, responsive, and interactive user experience, supporting real-time collaboration and productivity features. Here’s a one-page summary of the frontend architecture and key components:

## 1. Technology Stack
- **Bootstrap 5.3**: Core CSS framework for responsive layouts and UI components.
- **Font Awesome**: Icon library for rich visual elements.
- **Vanilla JavaScript**: Handles interactivity, dynamic UI updates, and API calls.
- **Socket.IO Client**: Enables real-time messaging, notifications, and live updates.

## 2. Template Structure
- **Jinja2 Templates**: Server-rendered HTML with dynamic data from Flask.
- **Modular Organization**: Templates grouped by feature for maintainability:
  - `main/` – Landing, about, contact
  - `auth/` – Login, register, forgot password
  - `admin/` – Admin dashboard, user/department management, analytics
  - `user/` – Profile, settings, edit profile
  - `tasks/` – Kanban board, task list, create/edit/view task
  - `chat/` – Direct and group chat interfaces
  - `meetings/` – Meeting list, create/edit/view meeting
  - `dashboard/` – User dashboard, analytics, calendar, notifications
  - `errors/` – Custom error pages (403, 404, 500)
- **Base Template**: `base.html` provides global layout, navigation, and asset loading.

## 3. Static Assets
- **CSS**: Custom styles in `static/css/main.css` extend Bootstrap for branding and UI tweaks.
- **Images**: Logos, avatars, and uploads stored in `static/images/` and `static/uploads/` (organized by type).
- **JS**: Client-side scripts for interactivity and Socket.IO integration (in `static/js/` if present).

## 4. Real-time Features
- **Chat**: Live messaging, typing indicators, online status, and file sharing via Socket.IO.
- **Notifications**: Real-time alerts for tasks, meetings, and system events.
- **Dashboard Updates**: Live activity feed and analytics refresh.

## 5. User Experience
- **Responsive Design**: Mobile-friendly layouts and touch support.
- **Kanban Board**: Drag-and-drop task management with color-coded priorities.
- **Calendar Integration**: Visual scheduling for tasks and meetings.
- **Rich Forms**: Interactive forms for login, registration, task creation, and meeting scheduling.
- **File Uploads**: Drag-and-drop support for attachments and profile pictures.
- **Accessibility**: Semantic HTML and ARIA attributes for usability.

## 6. Integration Points
- **API Calls**: JavaScript fetches data from Flask REST endpoints for dynamic updates.
- **AI Features**: Task generation and summarization via integrated APIs (if enabled).
- **External Calendars**: Google Calendar and holiday API integration for scheduling.

## 7. Customization & Theming
- **Organization Branding**: Custom logos, color palettes, and themes per organization.
- **User Preferences**: Theme selection, notification settings, and profile customization.

---

**In summary:**
FlowDeck’s frontend combines Bootstrap, Jinja2, and JavaScript for a seamless, real-time workflow experience. The modular template structure and static assets support rapid development and easy customization. For details, see the `app/templates/` and `app/static/` directories.

---

