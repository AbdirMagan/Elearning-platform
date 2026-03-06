# 🪟 Complete Windows Setup Guide

## Prerequisites

✅ Windows 10 or 11  
✅ Python 3.10 or higher  
✅ Windows Terminal (recommended) or PowerShell  
✅ Text editor (VS Code, Notepad++, or Notepad)

## Step-by-Step Installation

### Step 1: Extract the Project

1. Extract `elearning-platform.tar.gz` or the project folder
2. Open Windows Terminal or PowerShell
3. Navigate to the project:

```powershell
cd C:\Users\YourUsername\Downloads\elearning-platform
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it (you'll see (venv) in your prompt)
venv\Scripts\activate
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install packages
pip install Django==5.0.1 django-environ==0.11.2 dj-database-url==2.1.0 requests==2.31.0 django-crispy-forms>=2.3 crispy-bootstrap5==2024.10 Pillow django-cors-headers==4.3.1 python-decouple==3.8 python-dotenv==1.0.1 django-debug-toolbar==4.2.0 coverage==7.4.1 whitenoise==6.6.0
```

### Step 4: Configure Environment

```powershell
# Copy environment template
copy .env.example .env

# Edit with Notepad
notepad .env
```

**Update .env with these settings:**

```
# Django Settings
SECRET_KEY=change-this-to-a-long-random-string-1234567890
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite - automatic, no config needed!)

# WaafiPay (Get from dashboard.waafipay.com)
WAAFIPAY_MERCHANT_ID=your_merchant_id
WAAFIPAY_API_USER_ID=your_api_user_id
WAAFIPAY_API_KEY=your_api_key
WAAFIPAY_MODE=sandbox
WAAFIPAY_CALLBACK_URL=http://localhost:8000/payments/callback/

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Save and close Notepad**

### Step 5: Fix Celery Import (Important!)

```powershell
notepad elearning\__init__.py
```

**Replace content with:**

```python
# Celery is optional
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    pass
```

**Save and close**

### Step 6: Create Database

```powershell
# Delete old database if exists
del db.sqlite3 -ErrorAction SilentlyContinue

# Create migrations
python manage.py makemigrations users
python manage.py makemigrations courses
python manage.py makemigrations payments

# Apply migrations
python manage.py migrate
```

### Step 7: Create Admin User

```powershell
python manage.py createsuperuser
```

**Enter when prompted:**
- Email: your-email@example.com
- Username: admin (or any username)
- First name: (optional)
- Last name: (optional)
- Password: (choose a strong password)
- Password (again): (confirm)

### Step 8: Create Media Directories

```powershell
mkdir media\courses\thumbnails -Force
mkdir media\courses\videos -Force
mkdir media\courses\materials -Force
mkdir media\profile_pics -Force
```

### Step 9: Collect Static Files

```powershell
python manage.py collectstatic --noinput
```

### Step 10: Run the Server! 🎉

```powershell
python manage.py runserver
```

**Visit:** http://127.0.0.1:8000

## What You Should See

✅ Homepage with "Learn Without Limits"  
✅ Navigation menu working  
✅ Login/Register links visible  

## First Time Usage

### 1. Access Admin Panel

Visit: http://127.0.0.1:8000/admin  
Login: Use credentials you created in Step 7

### 2. Create Sample Data

Follow the [SAMPLE_DATA_GUIDE.md](SAMPLE_DATA_GUIDE.md) to:
- Create categories
- Add courses
- Create lessons
- Test the platform

### 3. Test as Student

1. **Register:** http://127.0.0.1:8000/users/register/
2. **Browse Courses:** http://127.0.0.1:8000/courses/
3. **Enroll in a course**
4. **Test payment flow**

## Common Windows Issues & Solutions

### Issue 1: "python not recognized"

**Solution:**
```powershell
# Use full path
py -m venv venv
py manage.py runserver
```

Or install Python from python.org and check "Add to PATH"

### Issue 2: "Access Denied" or Permission Errors

**Solution:**
```powershell
# Run Terminal as Administrator
# Right-click Windows Terminal → Run as Administrator
```

### Issue 3: Port 8000 Already in Use

**Solution:**
```powershell
# Use different port
python manage.py runserver 8001

# Then visit: http://127.0.0.1:8001
```

### Issue 4: Execution Policy Error

**Solution:**
```powershell
# Run once as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 5: Database Locked

**Solution:**
```powershell
# Close all Django connections
# Delete database
del db.sqlite3
# Recreate
python manage.py migrate
```

### Issue 6: Static Files Not Loading

**Solution:**
```powershell
python manage.py collectstatic --clear --noinput
```

### Issue 7: Module Not Found Errors

**Solution:**
```powershell
# Make sure venv is activated (you should see (venv))
venv\Scripts\activate

# Reinstall packages
pip install -r requirements-windows.txt
```

## Daily Usage Commands

### Starting Development

```powershell
# 1. Navigate to project
cd C:\Users\YourUsername\Downloads\elearning-platform

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Run server
python manage.py runserver
```

### Stopping the Server

```
Press Ctrl+C in the terminal
```

### Deactivating Virtual Environment

```powershell
deactivate
```

## Project Structure (Windows Paths)

```
elearning-platform\
├── venv\                      # Virtual environment
├── elearning\                 # Main project
│   ├── __init__.py
│   ├── settings.py           # Configuration
│   ├── urls.py               # URL routes
│   └── wsgi.py
├── users\                     # User management
├── courses\                   # Course system
├── payments\                  # Payment processing
├── templates\                 # HTML templates
├── static\                    # CSS, JS files
├── media\                     # Uploaded files
├── db.sqlite3                 # Database file
├── manage.py                  # Django commands
├── requirements-windows.txt   # Dependencies
└── .env                       # Configuration (create this)
```

## Useful Commands Reference

```powershell
# Activate environment (always do first!)
venv\Scripts\activate

# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

## Testing WaafiPay Integration

### Get WaafiPay Credentials

1. Visit: https://dashboard.waafipay.com
2. Sign up for merchant account
3. Go to Settings → API
4. Copy credentials to .env

### Test Payment

1. Create a course with price in admin
2. Register as student
3. Try to purchase course
4. Use test phone: +252612345678
5. Complete payment in sandbox

## Troubleshooting Checklist

If something doesn't work:

- [ ] Is virtual environment activated? (see `(venv)` in prompt)
- [ ] Did you run migrations? (`python manage.py migrate`)
- [ ] Is .env file configured?
- [ ] Did you create superuser?
- [ ] Are static files collected?
- [ ] Is server running without errors?
- [ ] Did you create sample data?

## Getting Help

1. **Check terminal for errors** - Read the error messages
2. **Review this guide** - Follow steps carefully
3. **Check logs** - Look at terminal output
4. **Read documentation** - See DOCUMENTATION.md
5. **Search error messages** - Google the specific error

## Next Steps

After successful installation:

1. ✅ Create sample categories and courses
2. ✅ Test all features as student
3. ✅ Configure WaafiPay credentials
4. ✅ Test payment flow in sandbox
5. ✅ Customize templates (optional)
6. ✅ Add your branding
7. ✅ Deploy to production (see DEPLOYMENT.md)

## Quick Tips

💡 **Always activate venv first** before running any commands  
💡 **Use Ctrl+C to stop the server** - don't just close the terminal  
💡 **Keep terminal open** while testing the website  
💡 **Check http://127.0.0.1:8000/admin** for management  
💡 **Use SQLite for development** - PostgreSQL only needed for production  

## Success! 🎉

If you can access http://127.0.0.1:8000 and see the homepage, you're all set!

Your e-learning platform is now running on Windows! 🚀

---

**Need More Help?**

- Read: QUICKSTART.md
- Read: DOCUMENTATION.md  
- Read: SAMPLE_DATA_GUIDE.md
- Check: WaafiPay documentation

Happy coding! 💻
