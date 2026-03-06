# ⚡ Quick Start Guide

Get your E-Learning platform up and running in minutes!

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git
- Optional: PostgreSQL (for production)

## 5-Minute Setup

### Step 1: Clone or Download

```bash
# If using Git
git clone <your-repo-url>
cd elearning-platform

# Or download and extract the ZIP file
cd elearning-platform
```

### Step 2: Automated Setup (Recommended)

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

The script will:
- Create virtual environment
- Install all dependencies
- Set up database
- Create admin user
- Collect static files
- Create media directories

### Step 3: Manual Setup (Alternative)

If the automated setup doesn't work:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 4: Configure WaafiPay

Edit `.env` file:

```bash
# WaafiPay Sandbox Credentials (for testing)
WAAFIPAY_MERCHANT_ID=your_merchant_id
WAAFIPAY_API_USER_ID=your_api_user_id
WAAFIPAY_API_KEY=your_api_key
WAAFIPAY_MODE=sandbox
```

**Get Sandbox Credentials:**
1. Visit: https://sandbox.waafipay.net
2. Sign up for developer account
3. Copy API credentials

### Step 5: Run Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

## First Steps After Installation

### 1. Access Admin Panel

URL: **http://127.0.0.1:8000/admin**

Login with the superuser credentials you created.

### 2. Create Course Categories

Admin Panel → Categories → Add Category

Example categories:
- Programming
- Business
- Design
- Marketing
- Data Science

### 3. Create Your First Course

Admin Panel → Courses → Add Course

Required fields:
- Title
- Description
- Price (or mark as free)
- Category
- Status: Published

### 4. Add Lessons

Admin Panel → Lessons → Add Lesson

For each lesson:
- Title
- Course
- Video URL (upload video)
- Order

### 5. Test the Platform

#### As a Student:
1. Register: http://127.0.0.1:8000/users/register/
2. Browse courses
3. Try purchasing a course
4. Watch lessons
5. Complete quizzes

#### Test Payment Flow:
1. Browse to a paid course
2. Click "Enroll Now"
3. Use test phone number: `+252612345678`
4. Complete payment in sandbox

## Common Commands

### Development

```bash
# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test
```

### Database

```bash
# Backup database
python manage.py dumpdata > backup.json

# Restore database
python manage.py loaddata backup.json

# Reset database
python manage.py flush
```

## Project Structure Quick Reference

```
elearning-platform/
├── manage.py              # Django management
├── requirements.txt       # Dependencies
├── .env                  # Configuration (create from .env.example)
├── setup.sh              # Setup script
│
├── elearning/            # Main project
│   └── settings.py       # Settings
│
├── users/                # User management
├── courses/              # Course management
├── payments/             # Payment processing
│
├── templates/            # HTML templates
├── static/              # CSS, JS, images
└── media/               # User uploads
```

## Default URLs

| URL | Description |
|-----|-------------|
| `/` | Homepage |
| `/courses/` | Course list |
| `/users/register/` | Register |
| `/users/login/` | Login |
| `/users/dashboard/` | Student dashboard |
| `/admin/` | Admin panel |

## Environment Variables

### Required

```bash
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

WAAFIPAY_MERCHANT_ID=your_id
WAAFIPAY_API_USER_ID=your_user_id
WAAFIPAY_API_KEY=your_key
```

### Optional

```bash
# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Database (defaults to SQLite)
DATABASE_URL=postgresql://user:pass@localhost/db
```

## Testing WaafiPay Integration

### Sandbox Test Numbers

```
Success: +252612345678
Insufficient Balance: +252612345679
Invalid Account: +252612345680
```

### Test Flow

1. Create a course with price > $0
2. Register as a student
3. Go to course detail page
4. Click "Enroll Now"
5. Enter test phone number
6. Check payment status
7. Verify enrollment in dashboard

## Troubleshooting

### Port Already in Use

```bash
# Change port
python manage.py runserver 8001
```

### Migrations Error

```bash
# Delete db.sqlite3
rm db.sqlite3

# Delete migration files
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --clear --noinput

# Check settings
# STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### Cannot Upload Files

```bash
# Create media directories
mkdir -p media/courses/thumbnails
mkdir -p media/courses/videos

# Fix permissions
chmod -R 755 media/
```

## Next Steps

1. **Customize**: Edit templates and styles
2. **Add Content**: Create courses, lessons, quizzes
3. **Test Payments**: Use sandbox mode
4. **Go Live**: Switch to production mode
5. **Deploy**: Follow DEPLOYMENT.md guide

## Getting Help

- **Documentation**: See DOCUMENTATION.md
- **WaafiPay**: See WAAFIPAY_INTEGRATION.md
- **Deployment**: See DEPLOYMENT.md
- **Issues**: Check troubleshooting section

## Important Notes

⚠️ **Before Production:**
- Change SECRET_KEY
- Set DEBUG=False
- Use PostgreSQL database
- Configure proper email backend
- Set up HTTPS
- Use production WaafiPay credentials

✅ **Security Checklist:**
- [ ] Strong SECRET_KEY
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configured
- [ ] Database secured
- [ ] File upload limits set
- [ ] HTTPS enabled
- [ ] Backups configured

## Quick Tips

💡 **Development:**
- Use SQLite for local development
- Keep DEBUG=True locally
- Use sandbox WaafiPay credentials

💡 **Content Creation:**
- Start with free courses to test
- Add preview lessons
- Use high-quality thumbnails
- Write clear descriptions

💡 **Payment Testing:**
- Test all payment scenarios
- Verify callbacks work
- Check transaction logs
- Test refund process

## Support

Need help? Check:
1. README.md - Project overview
2. DOCUMENTATION.md - Complete documentation
3. WAAFIPAY_INTEGRATION.md - Payment integration
4. DEPLOYMENT.md - Production deployment

Happy Learning! 🎓
