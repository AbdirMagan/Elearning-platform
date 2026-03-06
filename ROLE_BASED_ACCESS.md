# 🔐 Role-Based Access Control Guide

## Overview

The e-learning platform now has comprehensive role-based access control with three distinct user types: **Administrator**, **Instructor**, and **Student**. Each role has specific permissions and access levels.

## User Roles & Permissions

### 👑 Administrator (Admin)

**Full platform control** - Can manage everything

#### Permissions:
✅ **User Management**
- View all users
- Create, edit, delete users
- Change user roles
- Activate/deactivate accounts

✅ **Course Management**
- View all courses (any status)
- Approve/reject pending courses
- Edit any course
- Delete any course
- Manage categories

✅ **Financial Management**
- View all transactions
- Process refunds
- View revenue reports
- Access financial analytics

✅ **Platform Management**
- Access admin dashboard
- View platform statistics
- Manage site settings
- View all enrollments

#### Dashboard Features:
- Platform-wide statistics
- Pending course approvals
- Recent enrollments
- Recent transactions
- User management interface

### 👨‍🏫 Instructor (Teacher)

**Course creation and student management** - Can only access own courses

#### Permissions:
✅ **Course Management**
- Create new courses
- Edit own courses only
- Add/edit lessons to own courses
- Add course materials
- Create quizzes
- View course statistics

✅ **Student Management**
- View students enrolled in own courses
- Track student progress in own courses
- View student completion rates

✅ **Financial Tracking**
- View revenue from own courses
- View transaction history for own courses

❌ **Cannot Do:**
- Edit other instructors' courses
- Delete any courses
- Approve courses
- View all platform users
- Access other instructors' student data
- Process refunds

#### Dashboard Features:
- Own course statistics
- Total students across all courses
- Revenue from own courses
- Student list for each course
- Course management tools

### 👨‍🎓 Student

**Learning focused** - Can only enroll and learn

#### Permissions:
✅ **Course Access**
- Browse all published courses
- Enroll in courses (free or paid)
- Access enrolled course content
- Watch video lessons
- Download course materials

✅ **Learning Activities**
- Take quizzes
- Track own progress
- View own enrollments
- Submit course reviews

✅ **Account Management**
- Update own profile
- View own transaction history
- Request refunds for own purchases

❌ **Cannot Do:**
- Create courses
- Edit any course content
- View other students' data
- Access instructor dashboard
- Access admin features
- Approve courses

#### Dashboard Features:
- Enrolled courses
- Progress tracking
- Course recommendations
- Learning statistics

## Access Control Implementation

### Decorators

The platform uses custom decorators to restrict access:

```python
from users.decorators import admin_required, instructor_required, student_required

@admin_required
def admin_only_view(request):
    # Only admins can access

@instructor_required
def instructor_only_view(request):
    # Only instructors and admins can access

@student_required
def student_only_view(request):
    # Only students can access
```

### Permission Checking

```python
from users.permissions import RolePermissionMixin

# Check if user can edit a course
if RolePermissionMixin.can_edit_course(user, course):
    # Allow editing

# Check if user can view students
if RolePermissionMixin.can_view_students(user, course):
    # Show student list
```

## URL Structure by Role

### Admin URLs
```
/users/admin/dashboard/                    # Admin dashboard
/users/admin/users/                        # Manage users
/users/admin/course/<id>/approve/          # Approve courses
/admin/                                    # Django admin panel
```

### Instructor URLs
```
/users/instructor/dashboard/               # Instructor dashboard
/users/instructor/course/<slug>/students/  # View course students
/admin/courses/course/add/                 # Create course
/admin/courses/course/<id>/change/         # Edit own course
```

### Student URLs
```
/users/student/dashboard/                  # Student dashboard
/courses/                                  # Browse courses
/course/<slug>/                           # View course details
/course/<slug>/lesson/<slug>/             # Access lesson
/payments/checkout/<slug>/                # Purchase course
```

## Creating Users with Different Roles

### Via Admin Panel

1. Go to: http://127.0.0.1:8000/admin/users/customuser/add/
2. Fill in details
3. Select **User type**: Student, Instructor, or Administrator
4. Save

### Via Django Shell

```python
python manage.py shell
```

```python
from users.models import CustomUser

# Create an Admin
admin = CustomUser.objects.create_user(
    email='admin@example.com',
    username='admin',
    password='password123',
    user_type='admin',
    first_name='Admin',
    last_name='User'
)

# Create an Instructor
instructor = CustomUser.objects.create_user(
    email='instructor@example.com',
    username='instructor',
    password='password123',
    user_type='instructor',
    first_name='John',
    last_name='Teacher'
)

# Create a Student (default)
student = CustomUser.objects.create_user(
    email='student@example.com',
    username='student',
    password='password123',
    user_type='student',
    first_name='Jane',
    last_name='Learner'
)
```

## Testing Role-Based Access

### Test as Admin

1. Create admin account (or use superuser)
2. Login at: /users/login/
3. You'll be redirected to: /users/admin/dashboard/
4. Try:
   - Viewing all users
   - Approving pending courses
   - Viewing all transactions

### Test as Instructor

1. Create instructor account
2. Login
3. You'll be redirected to: /users/instructor/dashboard/
4. Try:
   - Creating a course (goes to pending status)
   - Viewing your students
   - Trying to access admin features (should be blocked)

### Test as Student

1. Register new account (defaults to student)
2. Login
3. You'll be redirected to: /users/student/dashboard/
4. Try:
   - Browsing courses
   - Enrolling in free course
   - Purchasing paid course
   - Trying to access instructor/admin features (should be blocked)

## Security Features

### Automatic Redirection
- Users are automatically redirected to their role-specific dashboard
- Unauthorized access attempts show error messages

### Permission Checking
- All views check user permissions
- Database queries filtered by user role
- Instructors can only see their own data

### Error Messages
- Clear feedback when access is denied
- User-friendly permission error messages

## Workflow Examples

### 1. Instructor Creates Course

1. Instructor logs in
2. Goes to instructor dashboard
3. Clicks "Create New Course"
4. Fills in course details
5. Course status: **Pending**
6. Admin receives notification
7. Admin reviews and approves
8. Course status: **Published**
9. Students can now see and enroll

### 2. Student Enrolls in Course

1. Student browses courses
2. Finds interesting course
3. If free: Instant enrollment
4. If paid: Redirects to WaafiPay checkout
5. After payment: Automatic enrollment
6. Student can access course content
7. Progress tracked automatically
8. Instructor can see student in their list

### 3. Admin Manages Platform

1. Admin logs in
2. Sees platform statistics
3. Reviews pending courses
4. Approves/rejects courses
5. Manages users
6. Views all transactions
7. Processes refunds if needed

## Best Practices

### For Admins
✅ Review courses before approving
✅ Monitor transactions regularly
✅ Keep user accounts organized
✅ Process refund requests promptly

### For Instructors
✅ Only access your own courses
✅ Keep student data confidential
✅ Update course content regularly
✅ Respond to student needs

### For Students
✅ Complete enrolled courses
✅ Leave honest reviews
✅ Report issues promptly
✅ Respect course materials

## Troubleshooting

### "Access Denied" Errors

**Problem**: User trying to access restricted page
**Solution**: Check user role and permissions

### Instructor Can't See Students

**Problem**: Instructor accessing wrong course
**Solution**: Only instructors can see students in their own courses

### Student Can't Create Course

**Problem**: Students attempting instructor actions
**Solution**: User must be promoted to instructor role by admin

### Course Not Appearing

**Problem**: Course status is "pending" or "draft"
**Solution**: Admin must approve course to publish

## Migration from Old System

If upgrading from previous version:

```python
python manage.py migrate

# Update existing users
from users.models import CustomUser

# Set all existing users to students by default
CustomUser.objects.filter(user_type__isnull=True).update(user_type='student')

# Promote specific users to instructors
CustomUser.objects.filter(email='instructor@example.com').update(user_type='instructor')

# Promote admins
CustomUser.objects.filter(is_superuser=True).update(user_type='admin')
```

## Summary

### Admin: Full Control
- Manage everything
- Approve courses
- View all data
- Process refunds

### Instructor: Course & Students
- Create courses
- Manage own courses
- View own students
- Track own revenue

### Student: Learn Only
- Browse & enroll
- Access content
- Track progress
- Submit reviews

This role-based system ensures data security, proper access control, and a clean user experience! 🔐
