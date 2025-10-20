# Feature Implementation Plan - FlowDeck Enhancements

**Date**: October 20, 2025  
**Status**: In Progress

## 📋 Overview

This document outlines the implementation plan for the requested enhancements to FlowDeck, including chat improvements, leave management, calendar integration, and UI/UX enhancements.

---

## ✅ Completed Features

### 1. Searchable Assignee Dropdown ✅
**Status**: COMPLETED  
**Files Modified**: 
- `/app/templates/tasks/create.html`

**Implementation**:
- ✅ Integrated Select2 library for enhanced dropdowns
- ✅ Custom formatting showing user avatar, name, email, and department
- ✅ Search functionality across name, email, and department
- ✅ Applied to both assignees and tags dropdowns
- ✅ Responsive Bootstrap 5 theme

**Features**:
- Real-time search as you type
- Visual user cards in dropdown
- Multiple selection with badges
- Clear all functionality

---

### 2. Email Verification on Profile ✅
**Status**: COMPLETED  
**Files Modified**:
- `/app/templates/user/profile.html`
- `/app/routes/user.py`

**Implementation**:
- ✅ Email verification status banner on profile page
- ✅ Warning banner for unverified emails with resend button
- ✅ Success indicator for verified emails
- ✅ `resend_verification_email()` route added
- ✅ CSRF token protection on form
- ✅ Uses existing `is_email_verified` field from User model

**Features**:
- Visual status indicators (warning/success)
- One-click resend verification email
- Secure token generation
- Email utility integration ready

---

## 🚧 In Progress

### 3. Chat Read Receipts (Single/Double Tick)
**Status**: IN PROGRESS  
**Priority**: HIGH

#### Database Changes Needed:
```python
# Add to Message model
is_read = db.Column(db.Boolean, default=False)
read_at = db.Column(db.DateTime, nullable=True)
delivered_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Socket.IO Events Needed:
- `message_delivered` - Single tick ✓
- `message_read` - Double tick ✓✓

#### Implementation Steps:
1. **Database Migration**
   - Add columns to Message model
   - Run migration script

2. **Backend Socket Events**
   - Emit `message_delivered` when message reaches recipient
   - Emit `message_read` when recipient views message
   - Update message status in database

3. **Frontend Updates**
   - Add tick icons to message bubbles
   - Single gray tick when sent
   - Double gray ticks when delivered
   - Double blue ticks when read
   - Real-time update via Socket.IO

4. **Visual Design**
   ```html
   <!-- Sent (gray) -->
   <i class="fas fa-check text-secondary"></i>
   
   <!-- Delivered (double gray) -->
   <i class="fas fa-check-double text-secondary"></i>
   
   <!-- Read (double blue) -->
   <i class="fas fa-check-double text-primary"></i>
   ```

**Files to Modify**:
- `app/models/messaging.py`
- `app/sockets/chat_events.py`
- `app/templates/chat/direct.html`
- Database migration script

---

## 📝 Planned Features

### 4. Online Status Indicator
**Priority**: HIGH  
**Complexity**: MEDIUM

#### Requirements:
- Green dot for online users
- Gray dot for offline users
- Real-time updates via Socket.IO
- Show near profile picture in chat header

#### Implementation:
1. **Database**:
   ```python
   # Add to User model
   is_online = db.Column(db.Boolean, default=False)
   last_seen = db.Column(db.DateTime, default=datetime.utcnow)
   ```

2. **Socket.IO Events**:
   - `user_online` - When user connects
   - `user_offline` - When user disconnects
   - `status_change` - Broadcast to relevant users

3. **Frontend**:
   ```html
   <div class="position-relative d-inline-block">
       <img src="profile.jpg" class="avatar">
       <span class="online-indicator {% if user.is_online %}online{% else %}offline{% endif %}"></span>
   </div>
   ```

4. **CSS**:
   ```css
   .online-indicator {
       position: absolute;
       bottom: 2px;
       right: 2px;
       width: 12px;
       height: 12px;
       border-radius: 50%;
       border: 2px solid white;
   }
   .online-indicator.online {
       background-color: #10b981; /* Green */
   }
   .online-indicator.offline {
       background-color: #6b7280; /* Gray */
   }
   ```

**Files to Create/Modify**:
- Migration script for database
- `app/sockets/chat_events.py`
- `app/templates/chat/direct.html`
- CSS in main.css

---

### 5. Typing Indicator (iPhone Style)
**Priority**: HIGH  
**Complexity**: MEDIUM

#### Requirements:
- Yellow/orange dots animation
- Show when user is typing
- Hide after 3 seconds of inactivity
- Bubble style like iPhone

#### Implementation:
1. **Socket.IO Events**:
   ```javascript
   socket.emit('typing_start', {room_id: roomId, user_name: userName});
   socket.emit('typing_stop', {room_id: roomId});
   ```

2. **Frontend HTML**:
   ```html
   <div class="typing-indicator" id="typingIndicator" style="display: none;">
       <div class="typing-bubble">
           <span class="typing-dot"></span>
           <span class="typing-dot"></span>
           <span class="typing-dot"></span>
       </div>
       <small class="text-muted ms-2"><span id="typingUsername"></span> is typing...</small>
   </div>
   ```

3. **CSS Animation**:
   ```css
   .typing-bubble {
       background: #f59e0b; /* Amber/Yellow */
       border-radius: 18px;
       padding: 12px 16px;
       display: inline-flex;
       gap: 4px;
   }
   
   .typing-dot {
       width: 8px;
       height: 8px;
       border-radius: 50%;
       background: white;
       animation: typing 1.4s infinite;
   }
   
   .typing-dot:nth-child(2) { animation-delay: 0.2s; }
   .typing-dot:nth-child(3) { animation-delay: 0.4s; }
   
   @keyframes typing {
       0%, 60%, 100% { transform: translateY(0); }
       30% { transform: translateY(-10px); }
   }
   ```

4. **JavaScript Logic**:
   ```javascript
   let typingTimer;
   const typingTimeout = 3000; // 3 seconds
   
   messageInput.addEventListener('input', () => {
       socket.emit('typing_start', {room_id, user_name});
       clearTimeout(typingTimer);
       typingTimer = setTimeout(() => {
           socket.emit('typing_stop', {room_id});
       }, typingTimeout);
   });
   ```

---

### 6. Fix Chat Footer Positioning
**Priority**: MEDIUM  
**Complexity**: LOW

#### Requirements:
- Footer should always be at bottom
- Works on `/chat/` and `/chat/direct/{id}`
- Responsive on all screen sizes

#### Implementation:
```css
/* Add to chat pages */
.chat-container {
    display: flex;
    flex-direction: column;
    min-height: calc(100vh - 60px); /* Subtract navbar height */
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

.chat-footer {
    margin-top: auto;
    border-top: 1px solid #e5e7eb;
    background: white;
    padding: 15px;
}
```

**Files to Modify**:
- `app/templates/chat/index.html`
- `app/templates/chat/direct.html`
- `app/static/css/main.css`

---

### 7. Calendar Holidays API Integration
**Priority**: MEDIUM  
**Complexity**: MEDIUM

#### Recommended API: Calendarific
**Why**: Free tier available, comprehensive holiday data, easy integration

#### Setup:
1. **Register**: https://calendarific.com/
2. **Get API Key**: Free tier includes 1000 requests/month
3. **API Endpoint**: 
   ```
   https://calendarific.com/api/v2/holidays
   ?api_key=YOUR_API_KEY
   &country=US
   &year=2025
   ```

#### Implementation:
1. **Backend Route**:
   ```python
   @bp.route('/calendar/holidays/<int:year>')
   @login_required
   def get_holidays(year):
       import requests
       api_key = current_app.config['CALENDARIFIC_API_KEY']
       country = current_user.organisation.country_code or 'US'
       
       response = requests.get(
           'https://calendarific.com/api/v2/holidays',
           params={'api_key': api_key, 'country': country, 'year': year}
       )
       holidays = response.json()['response']['holidays']
       return jsonify({'holidays': holidays})
   ```

2. **Frontend Integration**:
   ```javascript
   // Add to calendar view
   fetch(`/dashboard/calendar/holidays/${year}`)
       .then(r => r.json())
       .then(data => {
           data.holidays.forEach(holiday => {
               calendar.addEvent({
                   title: `🎉 ${holiday.name}`,
                   start: holiday.date.iso,
                   color: '#ef4444',
                   allDay: true,
                   className: 'holiday-event'
               });
           });
       });
   ```

3. **Visual Enhancement**:
   - Different color for holidays (red)
   - Icon prefix (🎉)
   - Tooltip with holiday description

**Files to Modify**:
- `.env` (add API key)
- `app/routes/dashboard.py`
- `app/templates/dashboard/calendar.html`
- `requirements.txt` (if using requests)

---

### 8. Leave Request System in Chat
**Priority**: HIGH  
**Complexity**: HIGH

#### Requirements:
- Icon alongside image upload icon
- Modal form for leave request
- Submit directly from chat
- Manager/Admin approval workflow

#### Implementation:
1. **Chat UI Addition**:
   ```html
   <div class="chat-input-actions">
       <button class="btn btn-sm btn-outline-secondary" title="Attach Image">
           <i class="fas fa-image"></i>
       </button>
       <button class="btn btn-sm btn-outline-primary" title="Request Leave" 
               data-bs-toggle="modal" data-bs-target="#leaveRequestModal">
           <i class="fas fa-calendar-times"></i>
       </button>
   </div>
   ```

2. **Modal Form**:
   ```html
   <div class="modal fade" id="leaveRequestModal">
       <div class="modal-dialog">
           <div class="modal-content">
               <div class="modal-header">
                   <h5><i class="fas fa-calendar-times me-2"></i>Request Leave</h5>
               </div>
               <div class="modal-body">
                   <form id="leaveRequestForm">
                       <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                       <select name="leave_type" class="form-select mb-3">
                           <option value="sick">Sick Leave</option>
                           <option value="casual">Casual Leave</option>
                           <option value="vacation">Vacation</option>
                       </select>
                       <input type="date" name="start_date" class="form-control mb-3">
                       <input type="date" name="end_date" class="form-control mb-3">
                       <textarea name="reason" class="form-control" rows="3"></textarea>
                   </form>
               </div>
               <div class="modal-footer">
                   <button type="submit" class="btn btn-primary">Submit Request</button>
               </div>
           </div>
       </div>
   </div>
   ```

3. **Backend Processing**:
   - Same endpoint as regular leave request
   - Send notification to manager via chat
   - Show leave request card in chat

4. **Chat Message Type**:
   ```python
   # Add to Message model
   message_type = db.Column(db.String(20), default='text')  
   # Options: 'text', 'image', 'leave_request'
   metadata = db.Column(db.JSON)  # Store leave request details
   ```

**Files to Modify**:
- `app/templates/chat/direct.html`
- `app/sockets/chat_events.py`
- `app/models/messaging.py`
- Database migration

---

### 9. Leave Quota Management System
**Priority**: HIGH  
**Complexity**: HIGH

#### Requirements:
- Admin sets manager leave quotas
- Manager sets employee leave quotas
- Track used vs. available leaves
- Show in profile and leave request form

#### Database Schema:
```python
# Add to User model
sick_leave_quota = db.Column(db.Integer, default=0)
casual_leave_quota = db.Column(db.Integer, default=0)
vacation_leave_quota = db.Column(db.Integer, default=0)

sick_leave_used = db.Column(db.Integer, default=0)
casual_leave_used = db.Column(db.Integer, default=0)
vacation_leave_used = db.Column(db.Integer, default=0)

# Calculated properties
@property
def sick_leave_remaining(self):
    return self.sick_leave_quota - self.sick_leave_used

@property
def casual_leave_remaining(self):
    return self.casual_leave_quota - self.casual_leave_used

@property
def vacation_leave_remaining(self):
    return self.vacation_leave_quota - self.vacation_leave_used
```

#### Admin Interface:
1. **Set Manager Quotas** (`/admin/users/<id>/leave-quota`):
   ```html
   <form method="POST">
       <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
       <div class="row">
           <div class="col-md-4">
               <label>Sick Leave Days</label>
               <input type="number" name="sick_leave_quota" class="form-control">
           </div>
           <div class="col-md-4">
               <label>Casual Leave Days</label>
               <input type="number" name="casual_leave_quota" class="form-control">
           </div>
           <div class="col-md-4">
               <label>Vacation Days</label>
               <input type="number" name="vacation_leave_quota" class="form-control">
           </div>
       </div>
   </form>
   ```

2. **Manager Interface** (`/manager/team/<user_id>/leave-quota`):
   - Same form but only for team members
   - Can't exceed their own quota

3. **User Profile Display**:
   ```html
   <div class="leave-quota-card">
       <h6>Leave Balance</h6>
       <div class="row text-center">
           <div class="col-4">
               <div class="quota-circle">
                   <span class="quota-remaining">{{ user.sick_leave_remaining }}</span>
                   <span class="quota-total">/{{ user.sick_leave_quota }}</span>
               </div>
               <small>Sick Leave</small>
           </div>
           <div class="col-4">
               <div class="quota-circle">
                   <span class="quota-remaining">{{ user.casual_leave_remaining }}</span>
                   <span class="quota-total">/{{ user.casual_leave_quota }}</span>
               </div>
               <small>Casual Leave</small>
           </div>
           <div class="col-4">
               <div class="quota-circle">
                   <span class="quota-remaining">{{ user.vacation_leave_remaining }}</span>
                   <span class="quota-total">/{{ user.vacation_leave_quota }}</span>
               </div>
               <small>Vacation</small>
           </div>
       </div>
   </div>
   ```

4. **Validation on Leave Request**:
   ```python
   @bp.route('/leave-requests/create', methods=['POST'])
   def create_leave_request():
       leave_type = request.form.get('leave_type')
       days = calculate_days(start_date, end_date)
       
       # Check quota
       if leave_type == 'sick':
           if current_user.sick_leave_remaining < days:
               flash('Insufficient sick leave balance!', 'danger')
               return redirect(url_for('user.create_leave_request'))
       # Similar for other types
   ```

**Files to Create/Modify**:
- Database migration script
- `app/models/user.py`
- `app/routes/admin.py`
- `app/routes/user.py`
- `app/templates/admin/set_leave_quota.html`
- `app/templates/user/profile.html`

---

## 🎨 UI/UX Enhancements Summary

### Visual Consistency
All new features follow the established design system:
- Purple gradient theme (#667eea to #764ba2)
- Glass morphism cards
- Smooth animations
- Responsive design
- Accessible color contrasts

### Icons Used
- 📧 Email verification: `fa-envelope`, `fa-check-circle`, `fa-exclamation-triangle`
- 👥 Assignees: `fa-users`, avatar circles
- ✓ Read receipts: `fa-check`, `fa-check-double`
- 🟢 Online status: Circle indicators with conditional colors
- ⚡ Typing: Animated dots in bubble
- 📅 Calendar: `fa-calendar-times` for leave requests
- 📊 Quota: Circular progress indicators

---

## 📦 Dependencies to Add

### Frontend Libraries:
```html
<!-- Select2 (Already added) -->
<link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
```

### Backend Packages:
```txt
# Add to requirements.txt
requests==2.31.0  # For API calls (if not already present)
```

### Environment Variables:
```bash
# Add to .env
CALENDARIFIC_API_KEY=your_api_key_here
SMTP_SERVER=smtp.gmail.com  # For email verification
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## 📅 Implementation Timeline

### Phase 1 (Current) - Days 1-2 ✅
- ✅ Searchable assignee dropdown
- ✅ Email verification on profile

### Phase 2 - Days 3-4
- 🚧 Chat read receipts
- 🚧 Online status indicator
- 🚧 Typing indicator

### Phase 3 - Days 5-6
- ⏳ Fix chat footer
- ⏳ Calendar API integration

### Phase 4 - Days 7-10
- ⏳ Leave request in chat
- ⏳ Leave quota management system

---

## 🧪 Testing Checklist

### Feature Testing:
- [ ] Search assignees by name, email, department
- [ ] Email verification resend works
- [ ] Read receipts update in real-time
- [ ] Online status shows correctly
- [ ] Typing indicator appears/disappears
- [ ] Chat footer stays at bottom
- [ ] Holidays display on calendar
- [ ] Leave requests work from chat
- [ ] Quota validation prevents over-booking

### Cross-Browser Testing:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### Responsive Testing:
- [ ] Mobile (320px - 767px)
- [ ] Tablet (768px - 1024px)
- [ ] Desktop (1025px+)

---

## 📝 Notes for Development

1. **Database Migrations**: Always backup database before running migrations
2. **Socket.IO Events**: Test with multiple clients simultaneously
3. **API Rate Limits**: Cache holiday data to avoid hitting Calendarific limits
4. **Leave Quota**: Consider fiscal year vs calendar year logic
5. **Security**: All forms have CSRF tokens
6. **Performance**: Use eager loading for related data
7. **Email Service**: Configure SMTP or use service like SendGrid

---

## 🆘 Support & Resources

- **Select2 Docs**: https://select2.org/
- **Calendarific API**: https://calendarific.com/api-documentation
- **Socket.IO Docs**: https://socket.io/docs/v4/
- **Flask-SocketIO**: https://flask-socketio.readthedocs.io/

---

*Last Updated: October 20, 2025*  
*Status: 2/9 Features Complete, 7 Remaining*
