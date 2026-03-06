from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import CustomUser
from .decorators import student_required, instructor_required, admin_required
from .permissions import RolePermissionMixin
from courses.models import Enrollment, Course


def register(request):
    """
    User registration view with email verification
    """
    if request.user.is_authenticated:
        return redirect('courses:home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'student'  # Default to student
            user.is_active = False  # Deactivate until email is verified
            user.save()
            
            # Create email verification
            from .models import EmailVerification
            verification = EmailVerification.objects.create(user=user)
            
            # Send verification email
            from .email_service import send_verification_email
            if send_verification_email(user, verification.verification_code):
                messages.success(
                    request,
                    f'Account created! Please check your email ({user.email}) for the verification code.'
                )
                return redirect('users:verify_email', user_id=user.id)
            else:
                messages.warning(
                    request,
                    'Account created but we could not send the verification email. Please contact support.'
                )
                return redirect('users:login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """
    User login view
    """
    if request.user.is_authenticated:
        return redirect('courses:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # username field contains email
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                
                # Redirect to next URL if provided
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('courses:home')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    """
    User logout view
    """
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('courses:home')


@login_required
def profile(request):
    """
    User profile view with update functionality
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Get user's enrolled courses
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'enrollments': enrollments,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def dashboard(request):
    """
    User dashboard showing enrolled courses and progress
    Role-based access: Students, Instructors, and Admins see different dashboards
    """
    user = request.user
    
    # Redirect based on user role
    if user.user_type == 'admin' or user.is_superuser:
        return redirect('users:admin_dashboard')
    elif user.user_type == 'instructor':
        return redirect('users:instructor_dashboard')
    else:  # student
        return redirect('users:student_dashboard')


@login_required
@student_required
def student_dashboard(request):
    """
    Student dashboard - view enrolled courses and progress
    """
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').prefetch_related('course__lessons')
    
    # User's enrollment requests
    try:
        from courses.models import EnrollmentRequest
        enrollment_requests = EnrollmentRequest.objects.filter(user=request.user).select_related('course').order_by('-created_at')[:5]
    except Exception:
        enrollment_requests = []
    
    context = {
        'enrollments': enrollments,
        'enrollment_requests': enrollment_requests,
    }
    
    return render(request, 'users/student_dashboard.html', context)


@login_required
@instructor_required
def instructor_dashboard(request):
    """
    Instructor dashboard - manage courses and view students
    """
    # Get instructor's courses
    courses = Course.objects.filter(
        instructor=request.user
    ).prefetch_related('enrollments')
    
    # Calculate stats
    total_students = Enrollment.objects.filter(
        course__instructor=request.user
    ).values('user').distinct().count()
    
    total_revenue = 0
    from payments.models import Transaction
    completed_transactions = Transaction.objects.filter(
        course__instructor=request.user,
        status='completed'
    )
    for trans in completed_transactions:
        total_revenue += trans.amount
    
    context = {
        'courses': courses,
        'total_students': total_students,
        'total_revenue': total_revenue,
        'total_courses': courses.count(),
    }
    
    return render(request, 'users/instructor_dashboard.html', context)


@login_required
@admin_required
def admin_dashboard(request):
    """
    Admin dashboard - overview of entire platform
    """
    from payments.models import Transaction
    
    # Get all stats
    total_users = CustomUser.objects.count()
    total_students = CustomUser.objects.filter(user_type='student').count()
    total_instructors = CustomUser.objects.filter(user_type='instructor').count()
    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(status='published').count()
    pending_courses = Course.objects.filter(status='pending').count()
    total_enrollments = Enrollment.objects.count()
    
    # Revenue stats
    total_revenue = 0
    completed_transactions = Transaction.objects.filter(status='completed')
    for trans in completed_transactions:
        total_revenue += trans.amount
    
    # Recent activities
    recent_enrollments = Enrollment.objects.select_related('user', 'course').order_by('-enrolled_at')[:10]
    recent_transactions = Transaction.objects.select_related('user', 'course').order_by('-created_at')[:10]
    pending_courses_list = Course.objects.filter(status='pending').select_related('instructor')[:10]
    
    # Pending enrollment requests
    try:
        from courses.models import EnrollmentRequest
        pending_enrollment_requests = EnrollmentRequest.objects.select_related('user', 'course').filter(status='pending').order_by('-created_at')[:10]
        pending_enrollment_count = EnrollmentRequest.objects.filter(status='pending').count()
    except Exception:
        pending_enrollment_requests = []
        pending_enrollment_count = 0
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_courses': total_courses,
        'published_courses': published_courses,
        'pending_courses': pending_courses,
        'total_enrollments': total_enrollments,
        'total_revenue': total_revenue,
        'recent_enrollments': recent_enrollments,
        'recent_transactions': recent_transactions,
        'pending_courses_list': pending_courses_list,
        'pending_enrollment_requests': pending_enrollment_requests,
        'pending_enrollment_count': pending_enrollment_count,
    }
    
    return render(request, 'users/admin_dashboard.html', context)


@login_required
@instructor_required
def instructor_students(request, course_slug):
    """
    View students enrolled in instructor's course
    """
    from courses.models import Course
    from django.shortcuts import get_object_or_404
    
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    
    enrollments = Enrollment.objects.filter(
        course=course
    ).select_related('user').order_by('-enrolled_at')
    
    context = {
        'course': course,
        'enrollments': enrollments,
    }
    
    return render(request, 'users/instructor_students.html', context)


@login_required
@admin_required
def admin_users_list(request):
    """
    Admin view to manage all users
    """
    users = CustomUser.objects.all().order_by('-created_at')
    
    # Filter by user type if specified
    user_type = request.GET.get('type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    context = {
        'users': users,
        'selected_type': user_type,
    }
    
    return render(request, 'users/admin_users_list.html', context)


@login_required
@admin_required  
def admin_approve_course(request, course_id):
    """
    Admin approve or reject course
    """
    from courses.models import Course
    from django.shortcuts import get_object_or_404
    
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            course.status = 'published'
            from django.utils import timezone
            course.published_at = timezone.now()
            course.save()
            messages.success(request, f'Course "{course.title}" has been approved and published.')
        elif action == 'reject':
            course.status = 'draft'
            course.save()
            messages.warning(request, f'Course "{course.title}" has been rejected.')
        
        return redirect('users:admin_dashboard')
    
    context = {
        'course': course,
    }
    
    return render(request, 'users/admin_approve_course.html', context)


@login_required
@admin_required
def admin_courses(request):
    """
    Admin view to manage all courses
    """
    from courses.models import Course
    
    courses = Course.objects.all().select_related('instructor', 'category').prefetch_related('lessons')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        courses = courses.filter(status=status_filter)
    
    context = {
        'courses': courses,
        'status_filter': status_filter,
    }
    
    return render(request, 'users/admin_courses.html', context)


@login_required
@admin_required
def admin_transactions(request):
    """
    Admin view to manage all transactions
    """
    from payments.models import Transaction
    
    transactions = Transaction.objects.all().select_related('user', 'course').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    context = {
        'transactions': transactions,
        'status_filter': status_filter,
    }
    
    return render(request, 'users/admin_transactions.html', context)


@login_required
@admin_required
def admin_courses(request):
    """
    Admin view to manage all courses - simplified interface
    """
    return render(request, 'users/admin_courses.html', {})


@login_required
@admin_required
def admin_transactions(request):
    """
    Admin view for all transactions
    """
    from payments.models import Transaction
    
    transactions = Transaction.objects.select_related('user', 'course').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    context = {
        'transactions': transactions,
        'selected_status': status,
    }
    
    return render(request, 'users/admin_transactions.html', context)


def verify_email(request, user_id):
    """
    Email verification view
    """
    try:
        from .models import CustomUser, EmailVerification
        user = CustomUser.objects.get(id=user_id)
        verification = user.email_verification
    except (CustomUser.DoesNotExist, EmailVerification.DoesNotExist):
        messages.error(request, 'Invalid verification link.')
        return redirect('users:login')
    
    if verification.is_verified:
        messages.info(request, 'Your email is already verified. Please log in.')
        return redirect('users:login')
    
    if request.method == 'POST':
        code = request.POST.get('verification_code', '').strip()
        
        if not code:
            messages.error(request, 'Please enter the verification code.')
        elif verification.is_expired():
            messages.error(request, 'Verification code has expired. Please request a new one.')
        elif verification.attempts >= 5:
            messages.error(request, 'Too many failed attempts. Please request a new verification code.')
        elif code == verification.verification_code:
            # Successful verification
            verification.is_verified = True
            verification.save()
            
            user.is_active = True
            user.is_verified = True
            user.save()
            
            # Send welcome email
            from .email_service import send_welcome_email
            send_welcome_email(user)
            
            messages.success(request, 'Email verified successfully! You can now log in.')
            return redirect('users:login')
        else:
            verification.attempts += 1
            verification.save()
            remaining = 5 - verification.attempts
            messages.error(request, f'Invalid verification code. {remaining} attempts remaining.')
    
    context = {
        'user': user,
        'verification': verification,
    }
    
    return render(request, 'users/verify_email.html', context)


def resend_verification(request, user_id):
    """
    Resend verification code
    """
    try:
        from .models import CustomUser
        user = CustomUser.objects.get(id=user_id)
        verification = user.email_verification
    except (CustomUser.DoesNotExist, EmailVerification.DoesNotExist):
        messages.error(request, 'Invalid request.')
        return redirect('users:login')
    
    if verification.is_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('users:login')
    
    # Generate new code
    verification.regenerate_code()
    
    # Send new code
    from .email_service import resend_verification_code
    if resend_verification_code(user, verification.verification_code):
        messages.success(request, f'New verification code sent to {user.email}')
    else:
        messages.error(request, 'Failed to send verification code. Please try again.')
    
    return redirect('users:verify_email', user_id=user.id)


@login_required
@admin_required
def admin_enrollment_requests(request):
    """
    Admin view to manage enrollment requests
    """
    from courses.models import EnrollmentRequest
    
    status_filter = request.GET.get('status', 'pending')
    
    requests_qs = EnrollmentRequest.objects.select_related('user', 'course', 'processed_by')
    
    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)
    
    requests_list = requests_qs.order_by('-created_at')
    
    context = {
        'enrollment_requests': requests_list,
        'status_filter': status_filter,
        'pending_count': EnrollmentRequest.objects.filter(status='pending').count(),
    }
    
    return render(request, 'users/admin_enrollment_requests.html', context)


@login_required
@admin_required
def process_enrollment_request(request, request_id):
    """
    Approve or reject enrollment request
    """
    from courses.models import EnrollmentRequest
    
    enroll_request = get_object_or_404(EnrollmentRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        if action == 'approve':
            enroll_request.approve(request.user, admin_notes)
            messages.success(
                request,
                f'Enrollment approved for {enroll_request.user.get_full_name()} in {enroll_request.course.title}'
            )
            # Notify student by email
            try:
                from .email_service import send_enrollment_request_notification
                send_enrollment_request_notification(enroll_request.user, enroll_request.course, 'approved', admin_notes)
            except Exception:
                pass
        elif action == 'reject':
            enroll_request.reject(request.user, admin_notes)
            messages.warning(
                request,
                f'Enrollment rejected for {enroll_request.user.get_full_name()}'
            )
            # Notify student by email
            try:
                from .email_service import send_enrollment_request_notification
                send_enrollment_request_notification(enroll_request.user, enroll_request.course, 'rejected', admin_notes)
            except Exception:
                pass
        
        return redirect('users:admin_enrollment_requests')
    
    context = {
        'enrollment_request': enroll_request,
    }
    
    return render(request, 'users/process_enrollment_request.html', context)
