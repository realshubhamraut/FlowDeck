# FlowDeck - Next Steps Guide

This document outlines the recommended steps to complete FlowDeck and take it to 100%.

---

## 📋 Overview

**Current Status:** 75% Complete  
**Backend:** 100% ✅  
**Frontend:** 45% 🟡  
**Testing:** 0% ❌

**What's Done:**
- All business logic and API endpoints
- Database with advanced features
- Real-time chat and notifications
- Dashboard, analytics, calendar pages
- Task list view
- Authentication and security
- Documentation

**What's Needed:**
- 30 HTML templates
- JavaScript enhancements
- Testing suite

---

## 🎯 Recommended Development Order

### Phase 1: Essential Task Templates (Priority: HIGH)
**Goal:** Make task management fully functional  
**Time Estimate:** 2-3 days

#### 1.1 Task Kanban Board
**File:** `app/templates/tasks/kanban.html`

**What it needs:**
- Drag-and-drop columns (To Do, In Progress, Done, Archived)
- Task cards with title, priority badge, assignees
- Quick status change functionality
- Filter by assignee, priority
- SortableJS integration for drag-drop

**Backend route:** Already exists at `app/routes/tasks.py` → `kanban_view()`

**Template structure:**
```html
{% extends "base.html" %}
{% block content %}
<div class="kanban-board">
    <div class="kanban-column" data-status="to_do">
        <h5>To Do</h5>
        {% for task in tasks_todo %}
            <div class="kanban-card" data-task-id="{{ task.id }}">
                <!-- Task card content -->
            </div>
        {% endfor %}
    </div>
    <!-- Repeat for other statuses -->
</div>
{% endblock %}
```

#### 1.2 Task Create Form
**File:** `app/templates/tasks/create.html`

**What it needs:**
- Task title input
- Description (rich text editor - Quill or TinyMCE)
- Priority dropdown
- Due date picker
- Assignee multi-select
- Department selector
- Deliverables dynamic fields
- File attachment upload

**Backend route:** Already exists at `app/routes/tasks.py` → `create_task()`

#### 1.3 Task Detail View
**File:** `app/templates/tasks/view.html`

**What it needs:**
- Task header with title, status, priority
- Assignees list with avatars
- Description display
- Deliverables checklist
- Comments section with replies
- Attachments list with download buttons
- Time logs table
- History timeline
- Edit/Delete buttons (permission-based)

**Backend route:** Already exists at `app/routes/tasks.py` → `view_task(task_id)`

#### 1.4 Task Edit Form
**File:** `app/templates/tasks/edit.html`

**What it needs:**
- Same as create form but pre-populated
- Status change dropdown
- Archive button

**Backend route:** Already exists at `app/routes/tasks.py` → `edit_task(task_id)`

---

### Phase 2: Chat Interface (Priority: HIGH)
**Goal:** Enable team communication  
**Time Estimate:** 2-3 days

#### 2.1 Chat Layout
**File:** `app/templates/chat/index.html`

**What it needs:**
- Two-column layout (channels sidebar + messages)
- Channel list with unread counts
- User list for direct messages
- Online status indicators
- Search bar
- Create channel button

**Backend route:** Already exists at `app/routes/chat.py` → `index()`

#### 2.2 Channel View
**File:** `app/templates/chat/channel.html`

**What it needs:**
- Message feed with infinite scroll
- Message input with file upload
- Typing indicators
- Online members list
- Channel info sidebar
- Message grouping by date

**Backend route:** Already exists at `app/routes/chat.py` → `channel(channel_id)`

#### 2.3 Direct Messages
**File:** `app/templates/chat/direct.html`

**What it needs:**
- Similar to channel view
- User profile header
- One-on-one conversation

**Backend route:** Already exists at `app/routes/chat.py` → `direct_message(user_id)`

#### 2.4 Create Channel
**File:** `app/templates/chat/create_channel.html`

**What it needs:**
- Channel name input
- Description textarea
- Member selection (multi-select)
- Private/public toggle
- Submit button

**Backend route:** Already exists at `app/routes/chat.py` → `create_channel()`

#### 2.5 Message Search
**File:** `app/templates/chat/search.html`

**What it needs:**
- Search input
- Results list with context
- Filter by channel/user
- Date range filter

**Backend route:** Already exists at `app/routes/chat.py` → `search_messages()`

---

### Phase 3: Admin Panel (Priority: MEDIUM)
**Goal:** Organization setup and management  
**Time Estimate:** 3-4 days

#### 3.1 Admin Dashboard
**File:** `app/templates/admin/dashboard.html`

**What it needs:**
- Organization overview stats
- Quick links to management sections
- Recent activity feed
- System health indicators

**Backend route:** Already exists at `app/routes/admin.py` → `dashboard()`

#### 3.2 Organization Settings
**File:** `app/templates/admin/organisation.html`

**What it needs:**
- Org name, logo, contact details
- Theme settings
- Email configuration
- Feature toggles

**Backend route:** Already exists at `app/routes/admin.py` → `organisation_settings()`

#### 3.3 User Management
**Files:** 
- `app/templates/admin/users.html` - User list
- `app/templates/admin/create_user.html` - Create form
- `app/templates/admin/edit_user.html` - Edit form

**What they need:**
- Users table with search/filter
- Role badges
- Active/inactive status
- Create/edit forms with all user fields
- Bulk actions

**Backend routes:** Already exist in `app/routes/admin.py`

#### 3.4 Department Management
**Files:**
- `app/templates/admin/departments.html` - Department list
- `app/templates/admin/create_department.html` - Create form
- `app/templates/admin/edit_department.html` - Edit form

**What they need:**
- Department hierarchy display
- Member count
- CRUD forms

**Backend routes:** Already exist in `app/routes/admin.py`

#### 3.5 Roles Management
**File:** `app/templates/admin/roles.html`

**What it needs:**
- Roles table
- Permission checkboxes
- Create/edit inline

**Backend route:** Already exists at `app/routes/admin.py` → `manage_roles()`

#### 3.6 Admin Analytics
**File:** `app/templates/admin/analytics.html`

**What it needs:**
- Organization-wide metrics
- Department comparison charts
- User productivity leaderboard
- Task completion trends

**Backend route:** Already exists at `app/routes/admin.py` → `analytics()`

---

### Phase 4: User Profile Pages (Priority: MEDIUM)
**Goal:** User self-service  
**Time Estimate:** 1-2 days

#### 4.1 User Profile View
**File:** `app/templates/user/profile.html`

**What it needs:**
- Profile picture
- User info display
- Task statistics
- Recent activity

**Backend route:** Already exists at `app/routes/user.py` → `profile()`

#### 4.2 Edit Profile
**File:** `app/templates/user/edit_profile.html`

**What it needs:**
- Profile picture upload
- Name, email, phone fields
- Bio textarea
- Save button

**Backend route:** Already exists at `app/routes/user.py` → `edit_profile()`

#### 4.3 User Settings
**File:** `app/templates/user/settings.html`

**What it needs:**
- Theme preference (light/dark)
- Email notification toggles
- Password change section
- Language selection (future)

**Backend route:** Already exists at `app/routes/user.py` → `settings()`

#### 4.4 Leave Requests
**Files:**
- `app/templates/user/leave_requests.html` - List
- `app/templates/user/create_leave_request.html` - Create form

**What they need:**
- Leave request calendar
- Status badges
- Create form with date range
- Document upload
- Approval workflow display

**Backend routes:** Already exist in `app/routes/user.py`

#### 4.5 View Other User
**File:** `app/templates/user/view_user.html`

**What it needs:**
- Public profile information
- Contact button
- Shared tasks

**Backend route:** Already exists at `app/routes/user.py` → `view_user(user_id)`

---

### Phase 5: Additional Auth Pages (Priority: MEDIUM)
**Goal:** Complete authentication flow  
**Time Estimate:** 1 day

#### 5.1 Forgot Password
**File:** `app/templates/auth/forgot_password.html`

**What it needs:**
- Email input
- Submit button
- Instructions text

**Backend route:** Already exists at `app/routes/auth.py` → `forgot_password()`

#### 5.2 Reset Password
**File:** `app/templates/auth/reset_password.html`

**What it needs:**
- Token verification display
- New password input
- Confirm password input
- Submit button

**Backend route:** Already exists at `app/routes/auth.py` → `reset_password(token)`

#### 5.3 Change Password
**File:** `app/templates/auth/change_password.html`

**What it needs:**
- Current password input
- New password input
- Confirm password input
- Submit button

**Backend route:** Already exists at `app/routes/auth.py` → `change_password()`

---

### Phase 6: Public Pages (Priority: LOW)
**Goal:** Marketing and information  
**Time Estimate:** 1 day

#### 6.1 About Page
**File:** `app/templates/main/about.html`

#### 6.2 Features Page
**File:** `app/templates/main/features.html`

#### 6.3 Pricing Page
**File:** `app/templates/main/pricing.html`

#### 6.4 Contact Page
**File:** `app/templates/main/contact.html`

**Backend routes:** Already exist in `app/routes/main.py`

---

### Phase 7: JavaScript Enhancements (Priority: MEDIUM)
**Goal:** Rich interactions  
**Time Estimate:** 2-3 days

#### 7.1 Kanban Drag-and-Drop
**File:** `app/static/js/kanban.js`

**Technology:** SortableJS
**Implementation:**
```javascript
// Initialize drag-drop
const sortables = document.querySelectorAll('.kanban-column');
sortables.forEach(column => {
    new Sortable(column, {
        group: 'kanban',
        animation: 150,
        onEnd: function(evt) {
            // Update task status via AJAX
            updateTaskStatus(evt.item.dataset.taskId, evt.to.dataset.status);
        }
    });
});
```

#### 7.2 Rich Text Editor
**File:** `app/static/js/editor.js`

**Technology:** Quill.js
**Implementation:**
```javascript
// Initialize editor
const quill = new Quill('#editor', {
    theme: 'snow',
    modules: {
        toolbar: [
            ['bold', 'italic', 'underline'],
            ['link', 'blockquote', 'code-block'],
            [{ list: 'ordered' }, { list: 'bullet' }]
        ]
    }
});
```

#### 7.3 Date/Time Pickers
**File:** `app/static/js/datetime.js`

**Technology:** Flatpickr
**Implementation:**
```javascript
flatpickr('.datepicker', {
    enableTime: true,
    dateFormat: 'Y-m-d H:i',
});
```

#### 7.4 Form Validation
**File:** `app/static/js/validation.js`

**Technology:** Native JavaScript
**Features:**
- Real-time field validation
- Error message display
- Submit button state management

#### 7.5 Chat Enhancements
**File:** `app/static/js/chat.js`

**Features:**
- Auto-scroll to bottom
- Message grouping
- Emoji picker
- File upload previews
- Read receipts UI

---

### Phase 8: Testing Suite (Priority: LOW-MEDIUM)
**Goal:** Ensure reliability  
**Time Estimate:** 3-5 days

#### 8.1 Unit Tests
**Directory:** `tests/unit/`

**Test files:**
- `test_models.py` - Test all model methods
- `test_utils.py` - Test utility functions
- `test_auth.py` - Test authentication logic

**Example:**
```python
def test_user_password_hashing():
    user = User(username='test', email='test@example.com')
    user.set_password('password123')
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')
```

#### 8.2 Integration Tests
**Directory:** `tests/integration/`

**Test files:**
- `test_routes.py` - Test all route endpoints
- `test_api.py` - Test API responses
- `test_permissions.py` - Test access control

**Example:**
```python
def test_create_task_requires_login(client):
    response = client.post('/tasks/create')
    assert response.status_code == 302  # Redirect to login
```

#### 8.3 Socket.IO Tests
**Directory:** `tests/sockets/`

**Test files:**
- `test_chat_events.py`
- `test_notification_events.py`

**Example:**
```python
def test_send_message(socketio_client):
    socketio_client.emit('send_message', {
        'content': 'Test message',
        'channel_id': 1
    })
    received = socketio_client.get_received()
    assert len(received) > 0
```

---

## 🛠️ Development Tools & Libraries

### Recommended for Templates

#### Bootstrap Components
- **Cards:** Pre-built card components
- **Forms:** Form controls with validation styles
- **Modals:** Popup dialogs
- **Dropdowns:** Select menus
- **Badges:** Status indicators

#### Font Awesome Icons
Already included via CDN. Use for:
- Action buttons (edit, delete, save)
- Status indicators
- Navigation items

### Recommended for JavaScript

#### SortableJS (Drag-and-Drop)
```html
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
```

#### Quill (Rich Text Editor)
```html
<link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
<script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>
```

#### Flatpickr (Date Picker)
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
```

#### Choices.js (Multi-Select)
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/choices.js/public/assets/styles/choices.min.css">
<script src="https://cdn.jsdelivr.net/npm/choices.js/public/assets/scripts/choices.min.js"></script>
```

---

## 📝 Template Development Guidelines

### 1. Always Extend Base Template
```html
{% extends "base.html" %}
{% block title %}Your Page Title{% endblock %}
{% block content %}
    <!-- Your content -->
{% endblock %}
```

### 2. Use Existing CSS Classes
The main.css file already has classes for:
- `.task-priority-{urgent|high|medium|low}`
- `.task-status-{to_do|in_progress|done|archived}`
- `.kanban-board`, `.kanban-column`, `.kanban-card`
- `.online-indicator`
- `.notification-badge`

### 3. Follow Bootstrap Conventions
- Use `.row` and `.col-*` for layouts
- Use `.card` for containers
- Use `.btn` for buttons
- Use `.form-control` for inputs

### 4. Handle Permissions
```html
{% if current_user.is_admin() %}
    <!-- Admin-only content -->
{% endif %}

{% if can_edit_task(task) %}
    <!-- Edit button -->
{% endif %}
```

### 5. Display Flash Messages
Already handled in base.html, but ensure you use:
```python
flash('Success message', 'success')
flash('Error message', 'danger')
flash('Info message', 'info')
```

---

## 🔄 Testing Workflow

### 1. Set Up Test Database
```python
# tests/conftest.py
@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
```

### 2. Run Tests
```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_models.py
```

### 3. Coverage Goals
- **Models:** 80%+ coverage
- **Routes:** 70%+ coverage
- **Utils:** 90%+ coverage

---

## 📊 Progress Tracking

### Template Checklist

**Tasks (5 templates)**
- [ ] kanban.html
- [ ] create.html
- [x] list.html (created)
- [ ] view.html
- [ ] edit.html

**Chat (5 templates)**
- [ ] index.html
- [ ] channel.html
- [ ] direct.html
- [ ] create_channel.html
- [ ] search.html

**Admin (10 templates)**
- [ ] dashboard.html
- [ ] organisation.html
- [ ] users.html
- [ ] create_user.html
- [ ] edit_user.html
- [ ] departments.html
- [ ] create_department.html
- [ ] edit_department.html
- [ ] roles.html
- [ ] analytics.html

**User (6 templates)**
- [ ] profile.html
- [ ] edit_profile.html
- [ ] settings.html
- [ ] leave_requests.html
- [ ] create_leave_request.html
- [ ] view_user.html

**Auth (3 templates)**
- [ ] forgot_password.html
- [ ] reset_password.html
- [ ] change_password.html

**Public (4 templates)**
- [ ] about.html
- [ ] features.html
- [ ] pricing.html
- [ ] contact.html

**Total:** 33 templates remaining (5 already created)

---

## 🚀 Quick Wins

Start with these for immediate impact:

### 1. Task Kanban Board (2-3 hours)
Most requested feature, backend ready, just needs HTML + SortableJS

### 2. Chat Interface (3-4 hours)
Socket.IO working, just needs message display layout

### 3. Task Create Form (1-2 hours)
Simple form, backend ready, high user value

### 4. User Profile View (1 hour)
Easy template, good for new contributors

---

## 📞 Getting Help

### Reference Existing Templates
- Look at `dashboard/index.html` for layout patterns
- Look at `tasks/list.html` for table structures
- Look at `auth/login.html` for form patterns

### Backend Route Reference
All routes have docstrings explaining:
- What data they provide
- What they expect
- What they return

Example:
```python
@bp.route('/tasks/<int:task_id>')
@login_required
def view_task(task_id):
    """
    Display task details.
    
    Provides: task object, comments, attachments, time_logs
    Expects: task_id in URL
    Returns: tasks/view.html template
    """
```

---

## 🎯 Success Criteria

### Phase 1 Complete When:
- [ ] All task pages accessible
- [ ] Kanban drag-drop works
- [ ] Task CRUD fully functional

### Phase 2 Complete When:
- [ ] Real-time chat working
- [ ] File sharing functional
- [ ] Search returns results

### Phase 3 Complete When:
- [ ] Admin can manage all resources
- [ ] CRUD operations work
- [ ] Analytics display correctly

### Phase 4 Complete When:
- [ ] Users can edit profiles
- [ ] Settings persist
- [ ] Leave requests work

### Project 100% Complete When:
- [ ] All 38 templates created
- [ ] JavaScript enhancements working
- [ ] 70%+ test coverage
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Documentation updated

---

## 🎉 Final Notes

**You're 75% there!** The hard part (backend, database, architecture) is done. The remaining work is primarily frontend HTML/CSS, which follows clear patterns from existing templates.

**Estimated Time to 100%:**
- Templates: 5-7 days
- JavaScript: 2-3 days
- Testing: 3-5 days
- **Total: 10-15 days of focused development**

**Best Approach:**
1. Start with Phase 1 (Tasks) - highest value
2. Move to Phase 2 (Chat) - second highest value
3. Complete Phases 3-6 as needed
4. Add JavaScript enhancements
5. Write tests last

Good luck! 🚀
