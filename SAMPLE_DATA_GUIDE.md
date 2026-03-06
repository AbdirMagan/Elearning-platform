# 📊 Sample Data Setup Guide

This guide will help you create sample data to test your e-learning platform.

## Quick Setup via Admin Panel

### 1. Access Admin Panel

```
http://127.0.0.1:8000/admin
```

Login with your superuser credentials.

### 2. Create Categories

**Admin → Courses → Categories → Add Category**

Create these categories:

1. **Programming**
   - Name: Programming
   - Slug: programming (auto-filled)
   - Icon: fa-code

2. **Business**
   - Name: Business
   - Slug: business
   - Icon: fa-briefcase

3. **Design**
   - Name: Design
   - Slug: design
   - Icon: fa-paint-brush

4. **Marketing**
   - Name: Marketing
   - Slug: marketing
   - Icon: fa-chart-line

5. **Data Science**
   - Name: Data Science
   - Slug: data-science
   - Icon: fa-database

### 3. Create an Instructor Account

**Admin → Users → Add User**

- Email: instructor@example.com
- Username: instructor
- User type: Instructor
- First name: John
- Last name: Doe
- Password: (set a password)

### 4. Create Sample Courses

**Admin → Courses → Add Course**

#### Course 1: Python for Beginners

- Title: Python Programming for Beginners
- Slug: python-for-beginners (auto-filled)
- Description: Learn Python from scratch with hands-on projects
- Instructor: Select the instructor you created
- Category: Programming
- Level: Beginner
- Language: English
- Duration: 8 hours
- Price: 49.99
- Is free: No
- Status: Published
- Is featured: Yes

#### Course 2: Web Design Fundamentals

- Title: Web Design Fundamentals
- Slug: web-design-fundamentals
- Description: Master HTML, CSS, and responsive design
- Instructor: Same instructor
- Category: Design
- Level: Beginner
- Price: 39.99
- Status: Published

#### Course 3: Free Introduction to Programming

- Title: Introduction to Programming
- Slug: intro-to-programming
- Description: Start your coding journey with this free course
- Instructor: Same instructor
- Category: Programming
- Level: Beginner
- Is free: Yes
- Status: Published
- Is featured: Yes

### 5. Add Lessons to Courses

**Admin → Courses → Lessons → Add Lesson**

For "Python for Beginners":

1. **Lesson 1**
   - Title: Introduction to Python
   - Course: Python for Beginners
   - Order: 1
   - Is preview: Yes (so non-enrolled users can see it)
   - Description: Learn what Python is and why it's popular

2. **Lesson 2**
   - Title: Variables and Data Types
   - Course: Python for Beginners
   - Order: 2
   - Description: Understanding variables, strings, numbers, and booleans

3. **Lesson 3**
   - Title: Control Flow
   - Course: Python for Beginners
   - Order: 3
   - Description: If statements, loops, and logical operators

4. **Lesson 4**
   - Title: Functions
   - Course: Python for Beginners
   - Order: 4
   - Description: Creating and using functions

### 6. Add Materials to Lessons

**Admin → Courses → Materials → Add Material**

- Lesson: Introduction to Python
- Title: Python Cheat Sheet
- File: Upload a PDF or any file

### 7. Create a Quiz (Optional)

**Admin → Courses → Quizzes → Add Quiz**

- Course: Python for Beginners
- Title: Python Basics Quiz
- Passing score: 70
- Time limit: 30 minutes
- Max attempts: 3

Then add questions to the quiz.

## Test the Website

### As a Student:

1. **Register a new account**
   - Go to: http://127.0.0.1:8000/users/register/
   - Create a student account

2. **Browse courses**
   - Visit: http://127.0.0.1:8000/courses/

3. **Enroll in free course**
   - Click on the free "Introduction to Programming" course
   - Click "Enroll Now"

4. **Purchase a paid course**
   - Click on "Python for Beginners"
   - Click "Buy Now"
   - Enter test phone: +252612345678
   - (In sandbox mode, use any number)

5. **Access your dashboard**
   - Go to: http://127.0.0.1:8000/users/dashboard/

6. **Watch lessons**
   - Click on an enrolled course
   - Watch preview lessons

### As an Admin:

1. **Monitor transactions**
   - Admin → Payments → Transactions

2. **Manage courses**
   - Admin → Courses → Courses

3. **View enrollments**
   - Admin → Courses → Enrollments

## Using Django Shell for Bulk Data

If you want to create lots of sample data quickly:

```python
python manage.py shell
```

```python
from users.models import CustomUser
from courses.models import Category, Course, Lesson
from decimal import Decimal

# Create an instructor
instructor = CustomUser.objects.create_user(
    email='instructor@example.com',
    username='instructor',
    password='password123',
    user_type='instructor',
    first_name='John',
    last_name='Doe'
)

# Create categories
categories = []
for name in ['Programming', 'Business', 'Design', 'Marketing', 'Data Science']:
    cat, created = Category.objects.get_or_create(name=name)
    categories.append(cat)

# Create courses
course_data = [
    {
        'title': 'Python for Beginners',
        'description': 'Learn Python from scratch',
        'category': categories[0],
        'price': Decimal('49.99'),
        'level': 'beginner',
        'is_free': False,
    },
    {
        'title': 'Introduction to Business',
        'description': 'Business fundamentals',
        'category': categories[1],
        'price': Decimal('29.99'),
        'level': 'beginner',
        'is_free': False,
    },
    {
        'title': 'Free Web Design',
        'description': 'Learn web design for free',
        'category': categories[2],
        'price': Decimal('0'),
        'level': 'beginner',
        'is_free': True,
    },
]

for data in course_data:
    course = Course.objects.create(
        instructor=instructor,
        status='published',
        **data
    )
    
    # Add 3 lessons to each course
    for i in range(1, 4):
        Lesson.objects.create(
            course=course,
            title=f'Lesson {i}: {course.title}',
            description=f'This is lesson {i}',
            order=i,
            is_preview=(i == 1)  # First lesson is preview
        )

print("Sample data created successfully!")
```

## Sample Data Tips

1. **Always set status to "published"** for courses to appear on the website
2. **Mark first lesson as preview** so visitors can see it
3. **Use realistic prices** like 29.99, 49.99, 99.99
4. **Add course thumbnails** for better visual appeal (upload images)
5. **Create varied content** - mix free and paid courses
6. **Test payment flow** in sandbox mode before going live

## Testing Payment Integration

### Sandbox Testing

1. **Use WaafiPay sandbox mode**
   - .env: `WAAFIPAY_MODE=sandbox`

2. **Test phone numbers**
   - Success: +252612345678
   - Any valid Somali number format

3. **Monitor callback**
   - Check terminal/logs for callback data
   - Verify enrollment is created

4. **Check transaction status**
   - Admin → Payments → Transactions
   - Should show "completed"

### Production Testing

Before going live:

1. Switch to production mode in .env
2. Use real WaafiPay credentials
3. Test with small amount
4. Verify real money transfer
5. Check enrollment works
6. Test refund process

## Common Issues

### Course not appearing?
- Check status is "published"
- Verify category exists
- Check instructor is set

### Can't enroll?
- Free courses should enroll immediately
- Paid courses need payment first

### Payment not working?
- Check WaafiPay credentials in .env
- Verify phone number format
- Check callback URL is accessible
- Review terminal logs for errors

## Next Steps

After creating sample data:

1. Test all user flows
2. Add more content
3. Upload actual course videos
4. Create real course materials
5. Test on mobile devices
6. Get feedback from test users
7. Deploy to production

Your platform is now ready for testing! 🚀
