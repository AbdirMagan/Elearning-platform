# 📚 E-Learning Platform - Complete Documentation

## Project Overview

A full-featured Django-based e-learning platform with WaafiPay payment integration, designed for online course delivery and management.

## 🏗️ Architecture

### Technology Stack
```
Backend:     Django 5.0+
Database:    PostgreSQL (Production) / SQLite (Development)
Payment:     WaafiPay API
Frontend:    Bootstrap 5
Auth:        Django Authentication System
Task Queue:  Celery + Redis (Optional)
Storage:     Local / AWS S3
```

### Project Structure
```
elearning-platform/
├── elearning/              # Main project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── celery.py          # Celery configuration
│
├── users/                  # User management app
│   ├── models.py          # CustomUser, Profile models
│   ├── views.py           # Authentication views
│   ├── forms.py           # Registration/login forms
│   ├── admin.py           # Admin configuration
│   └── signals.py         # Profile creation signals
│
├── courses/                # Course management app
│   ├── models.py          # Course, Lesson, Quiz, Enrollment models
│   ├── views.py           # Course browsing and learning views
│   ├── admin.py           # Course administration
│   └── urls.py            # Course URLs
│
├── payments/               # Payment processing app
│   ├── models.py          # Transaction, Refund models
│   ├── views.py           # Payment processing views
│   ├── waafipay.py        # WaafiPay integration service
│   ├── admin.py           # Payment administration
│   └── urls.py            # Payment URLs
│
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── courses/           # Course templates
│   ├── users/             # User templates
│   └── payments/          # Payment templates
│
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploads
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── setup.sh               # Setup script
└── manage.py              # Django management script
```

## 🔑 Key Features

### 1. User Management
- **Registration & Authentication**
  - Email-based authentication
  - User profiles with extended information
  - Role-based access (Student, Instructor, Admin)
  
- **Profile Management**
  - Profile picture upload
  - Bio and personal information
  - Social links
  - Email notification preferences

### 2. Course Management
- **Course Creation**
  - Rich course descriptions
  - Category organization
  - Pricing and discounts
  - Course thumbnails and promo videos
  - Difficulty levels (Beginner, Intermediate, Advanced)

- **Course Content**
  - Multiple lessons per course
  - Video lessons
  - Downloadable materials (PDFs, documents)
  - Course requirements and learning outcomes

- **Quizzes & Assessments**
  - Multiple quiz types (Single choice, Multiple choice, True/False)
  - Passing scores
  - Time limits
  - Multiple attempts
  - Progress tracking

### 3. Payment Integration (WaafiPay)
- **Payment Processing**
  - Secure payment initialization
  - Mobile wallet integration
  - Real-time payment verification
  - Automatic enrollment on successful payment

- **Transaction Management**
  - Complete transaction history
  - Payment status tracking
  - Refund requests
  - Transaction analytics

### 4. Learning Experience
- **Course Enrollment**
  - One-click enrollment for free courses
  - Secure payment for paid courses
  - Instant access after payment

- **Progress Tracking**
  - Lesson completion tracking
  - Overall course progress percentage
  - Quiz attempt history
  - Certificate issuance

- **Course Reviews**
  - 5-star rating system
  - Written reviews
  - Average rating calculation

## 📊 Database Models

### User Models
```python
CustomUser
├── email (unique)
├── user_type (student/instructor/admin)
├── phone_number
├── bio
├── profile_picture
└── is_verified

Profile (OneToOne with CustomUser)
├── social_links
├── preferences
└── location
```

### Course Models
```python
Category
└── name, slug, description

Course
├── title, slug, description
├── instructor (ForeignKey to CustomUser)
├── category (ForeignKey to Category)
├── price, discount_price
├── status (draft/pending/published)
├── level, language
└── statistics (enrollments, rating)

Lesson
├── course (ForeignKey to Course)
├── title, description
├── video_url, video_duration
├── order
└── is_preview

Material
├── lesson (ForeignKey to Lesson)
├── title, file
└── file_type, file_size

Quiz
├── course (ForeignKey to Course)
├── title, description
├── passing_score
└── time_limit

Question
├── quiz (ForeignKey to Quiz)
├── question_text
├── question_type
└── points

Answer
├── question (ForeignKey to Question)
├── answer_text
└── is_correct

Enrollment
├── user (ForeignKey to CustomUser)
├── course (ForeignKey to Course)
├── progress_percentage
└── completed_at

LessonProgress
├── enrollment (ForeignKey to Enrollment)
├── lesson (ForeignKey to Lesson)
├── is_completed
└── time_spent

Review
├── course (ForeignKey to Course)
├── user (ForeignKey to CustomUser)
├── rating (1-5)
└── comment
```

### Payment Models
```python
Transaction
├── transaction_id (UUID)
├── user (ForeignKey to CustomUser)
├── course (ForeignKey to Course)
├── amount, currency
├── status (pending/completed/failed)
├── waafipay_transaction_id
└── waafipay_response (JSON)

Refund
├── transaction (OneToOne with Transaction)
├── amount
├── reason
├── status
└── processed_by
```

## 🔄 Payment Flow

### 1. Course Purchase Initiation
```python
User clicks "Buy Now" 
  → Redirects to checkout page
  → User enters phone number
  → System creates Transaction record
```

### 2. Payment Processing
```python
Transaction created with status='pending'
  → WaafiPay API called
  → Payment initialized
  → User receives push notification on phone
  → User enters PIN to confirm
```

### 3. Payment Completion
```python
WaafiPay processes payment
  → Sends callback to our server
  → Transaction status updated to 'completed'
  → Enrollment automatically created
  → User gains access to course
```

### 4. Payment Verification
```python
User checks payment status
  → System verifies with WaafiPay
  → Updates transaction status
  → Confirms enrollment
```

## 🛠️ Installation & Setup

### Quick Start

```bash
# Clone repository
git clone <repo-url>
cd elearning-platform

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Configuration

Required environment variables:
```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# WaafiPay
WAAFIPAY_MERCHANT_ID=your-merchant-id
WAAFIPAY_API_USER_ID=your-api-user-id
WAAFIPAY_API_KEY=your-api-key
WAAFIPAY_MODE=sandbox
WAAFIPAY_CALLBACK_URL=http://localhost:8000/payments/callback/
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

Key steps:
1. Server setup (Ubuntu)
2. PostgreSQL configuration
3. Gunicorn setup
4. Nginx configuration
5. SSL certificate (Let's Encrypt)
6. WaafiPay production setup

## 🧪 Testing

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test courses
python manage.py test payments

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Manual Testing Checklist

**User Registration & Login**
- [ ] Register new user
- [ ] Login with credentials
- [ ] Password reset
- [ ] Profile update

**Course Browsing**
- [ ] View all courses
- [ ] Filter by category
- [ ] Search courses
- [ ] Sort courses

**Course Purchase**
- [ ] View course details
- [ ] Initiate payment
- [ ] Complete payment via WaafiPay
- [ ] Verify enrollment
- [ ] Access course content

**Learning Experience**
- [ ] Watch video lessons
- [ ] Download materials
- [ ] Take quizzes
- [ ] Track progress
- [ ] Submit review

## 📱 API Endpoints

### Authentication
```
POST /users/register/          - Register new user
POST /users/login/             - User login
POST /users/logout/            - User logout
GET  /users/profile/           - View/edit profile
GET  /users/dashboard/         - User dashboard
```

### Courses
```
GET  /                         - Homepage
GET  /courses/                 - List all courses
GET  /course/<slug>/           - Course details
GET  /course/<slug>/lesson/<slug>/  - Lesson detail
POST /course/<slug>/review/    - Add review
GET  /category/<slug>/         - Category courses
```

### Payments
```
GET  /payments/checkout/<slug>/     - Checkout page
POST /payments/initiate/<slug>/     - Initialize payment
GET  /payments/status/<uuid>/       - Payment status
POST /payments/callback/            - WaafiPay callback
GET  /payments/history/             - Transaction history
POST /payments/refund/<uuid>/       - Request refund
```

### Admin
```
GET  /admin/                   - Admin dashboard
```

## 🔐 Security Features

1. **Authentication & Authorization**
   - CSRF protection enabled
   - Secure password hashing (PBKDF2)
   - Session management
   - Role-based access control

2. **Payment Security**
   - Secure API communication
   - Transaction validation
   - IP address logging
   - Rate limiting

3. **Data Protection**
   - XSS protection
   - SQL injection prevention (ORM)
   - File upload validation
   - Secure file storage

4. **Production Security**
   - HTTPS enforcement
   - Secure cookies
   - Security headers
   - Regular updates

## 📈 Performance Optimization

1. **Database**
   - Database indexing on frequently queried fields
   - Select_related and prefetch_related for queries
   - Connection pooling

2. **Caching**
   - Redis caching for frequently accessed data
   - Template fragment caching
   - Static file compression

3. **Static Files**
   - WhiteNoise for static files
   - CDN for media files (S3)
   - Gzip compression

4. **Async Tasks**
   - Celery for background tasks
   - Email sending
   - Report generation
   - Video processing

## 🐛 Troubleshooting

### Common Issues

**1. Payment Callback Not Received**
```bash
# Check callback URL is accessible
# Verify CSRF exemption
# Check WaafiPay dashboard logs
# Test with ngrok for local development
```

**2. Database Migration Errors**
```bash
# Reset migrations
python manage.py migrate --fake
python manage.py migrate
```

**3. Static Files Not Loading**
```bash
# Collect static files
python manage.py collectstatic --clear

# Check STATIC_ROOT and STATIC_URL settings
```

**4. Media Files Not Uploading**
```bash
# Check MEDIA_ROOT permissions
chmod 755 media/

# Verify MEDIA_URL configuration
```

## 📊 Monitoring & Logging

### Logging Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'payments': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### Monitoring Tools
- Django Debug Toolbar (development)
- Sentry (error tracking)
- Google Analytics (usage analytics)
- New Relic (performance monitoring)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Write tests
5. Submit pull request

## 📝 License

MIT License - see LICENSE file

## 📞 Support

- Email: support@example.com
- Documentation: [Link to docs]
- Issues: [GitHub Issues]

## 🙏 Acknowledgments

- Django Framework
- WaafiPay Payment Gateway
- Bootstrap UI Framework
- All contributors

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [WaafiPay Documentation](https://docs.waafipay.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Version**: 1.0.0
**Last Updated**: 2024
**Maintainer**: Your Team
