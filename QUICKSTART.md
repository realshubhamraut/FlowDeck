# FlowDeck - Quick Start Guide

Get FlowDeck up and running in 5 minutes!

---

## 🚀 Quick Setup (Automated)

### For macOS/Linux:
```bash
chmod +x setup.sh
./setup.sh
```

### For Windows:
```cmd
setup.bat
```

The script will automatically:
- Create virtual environment
- Install dependencies
- Initialize database
- Seed demo data

---

## 📦 Manual Setup

If you prefer manual installation:

### 1. Clone and Navigate
```bash
cd FlowDeck
```

### 2. Create Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Initialize Database
```bash
python run.py init-db
python run.py seed
```

### 6. Run Application
```bash
python run.py
```

Visit: http://localhost:5000

---

## 🔑 Default Credentials

**Email:** admin@flowdeck.org  
**Password:** admin123

⚠️ **Change immediately in production!**

---

## 📋 First Steps After Login

### 1. Change Admin Password
- Click on your profile → Settings → Change Password

### 2. Update Organisation Details
- Go to Admin → Organisation
- Update name, logo, contact info

### 3. Create Departments
- Admin → Departments → Create Department
- Examples: Engineering, Design, Marketing

### 4. Add Users
- Admin → Users → Create User
- Assign roles and departments
- Users receive email with credentials

### 5. Create First Task
- Tasks → Create Task
- Add title, description, assignees
- Set priority and due date

### 6. Start Chatting
- Chat → Select user or channel
- Send messages, share files
- Create group channels

---

## 🎯 Key Features to Try

### Task Management
- **Kanban Board:** Tasks → View: Kanban
- **Calendar View:** Dashboard → Calendar
- **AI Task Generation:** Tasks → Create → Ask AI

### Real-time Chat
- **Direct Messages:** Chat → Select user
- **Group Channels:** Chat → Create Channel
- **Send Task Cards:** Share tasks in chat

### Analytics
- **User Dashboard:** See personal stats
- **Admin Analytics:** Organization-wide insights
- **Reports:** Export productivity data

### Notifications
- **Real-time Alerts:** Bell icon in navbar
- **Email Notifications:** Configurable in settings
- **Task Reminders:** Automatic deadline alerts

---

## 🔧 Configuration

### Email Setup (Gmail)
1. Enable 2FA on your Gmail account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### OpenAI API (Optional)
For AI task generation:
```env
OPENAI_API_KEY=sk-...
```
Get key from: https://platform.openai.com/api-keys

### Google Calendar (Optional)
```env
GOOGLE_CALENDAR_API_KEY=your-key
```

---

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database
rm -f flowdeck.db  # or delete manually
python run.py init-db
python run.py seed
```

### Port Already in Use
Edit `run.py` and change port:
```python
socketio.run(app, port=5001)  # Change from 5000 to 5001
```

### Email Not Sending
- Check SMTP settings in `.env`
- Verify Gmail App Password
- Check firewall/antivirus

### Socket.IO Not Connecting
- Clear browser cache
- Check browser console for errors
- Ensure eventlet is installed

---

## 📚 Learn More

### User Roles
- **Admin:** Full access, manage organization
- **Manager:** Manage team, assign tasks
- **Employee:** View and update own tasks

### Task Priorities
- **Urgent:** Critical, immediate action
- **High:** Important, near-term
- **Medium:** Normal priority
- **Low:** Can be delayed

### Task Statuses
- **To Do:** Not started
- **In Progress:** Being worked on
- **Done:** Completed
- **Archived:** Hidden from view

---

## 🎨 Customization

### Organisation Theme
- Admin → Organisation
- Choose color palette
- Upload logo
- Select theme (Light/Dark)

### User Preferences
- Profile → Settings
- Theme preference
- Notification settings
- Email preferences

---

## 📱 Mobile Access

FlowDeck is fully responsive:
- Access from any device
- Mobile-optimized interface
- Touch-friendly controls
- Can be installed as PWA

---

## 🔒 Security Best Practices

1. **Change Default Password** immediately
2. **Use Strong Passwords** for all users
3. **Enable Email Verification**
4. **Regular Backups** of database
5. **Update Dependencies** regularly
6. **Use HTTPS** in production
7. **Limit Admin Access**
8. **Review Audit Logs** periodically

---

## 🆘 Need Help?

- **Documentation:** See README.md
- **Issues:** Create GitHub issue
- **Email:** support@flowdeck.org

---

## ✅ Production Deployment

For production deployment:
1. Set `FLASK_ENV=production`
2. Use PostgreSQL/MySQL instead of SQLite
3. Set up Nginx reverse proxy
4. Use Gunicorn with multiple workers
5. Enable SSL/TLS (HTTPS)
6. Configure backup system
7. Set up monitoring and logging
8. Use Redis for Socket.IO

See README.md for detailed deployment guide.

---

**Happy organizing with FlowDeck! 🚀**
