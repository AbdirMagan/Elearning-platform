from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator

from users.decorators import student_required
from users.models import CustomUser
from .models import Course, Category, Lesson, Enrollment, LessonProgress, Review, Quiz, QuizAttempt
from payments.models import Transaction


# Find the home function and update it:

def home(request):
    """
    Homepage view with dynamic hero slides and announcements
    """
    from .models import HeroSlide, Announcement
    
    # Get active hero slides
    hero_slides = HeroSlide.objects.filter(is_active=True).order_by('order')[:5]
    
    # Get active announcements for homepage
    active_announcements = []
    announcements = Announcement.objects.filter(
        is_active=True,
        show_on_homepage=True
    ).order_by('-priority', '-created_at')
    
    for announcement in announcements:
        if announcement.is_currently_active():
            # Compute remaining days and hours for display (server-side fallback)
            from django.utils import timezone
            announcement.remaining_days = None
            announcement.remaining_hours = None
            if announcement.end_date:
                now = timezone.now()
                diff = announcement.end_date - now
                if diff.total_seconds() > 0:
                    # diff.days gives whole days, diff.seconds gives remainder seconds
                    days = diff.days
                    hours = diff.seconds // 3600
                else:
                    days = 0
                    hours = 0
                announcement.remaining_days = days
                announcement.remaining_hours = hours

            active_announcements.append(announcement)
    
    # Get featured courses
    featured_courses = Course.objects.filter(
        status='published',
        is_featured=True
    ).select_related('instructor', 'category').prefetch_related('reviews')[:6]
    
    # Get categories with course count
    categories = Category.objects.annotate(
        course_count=Count('courses', filter=Q(courses__status='published'))
    ).filter(course_count__gt=0)[:8]
    # Get Available Courses
    available_courses = Course.objects.filter(status='published').select_related('instructor', 'category').prefetch_related('reviews')[:6]

    # Get instructors (latest active instructors)
    instructors = CustomUser.objects.filter(user_type='instructor').order_by('-created_at')[:8]
    # Stats
    total_courses = Course.objects.filter(status='published').count()
    total_students = CustomUser.objects.filter(user_type='student').count()
    
    context = {
        'hero_slides': hero_slides,
        'announcements': active_announcements,
        'featured_courses': featured_courses,
        'categories': categories,
        'total_courses': total_courses,
        'total_students': total_students,
        'available_courses': available_courses,
        'instructors': instructors,
    }
    
    return render(request, 'courses/home.html', context)

def course_list(request):
    """
    List all courses with filtering and search
    """
    courses = Course.objects.filter(status='published').select_related('category', 'instructor')
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(instructor__first_name__icontains=search_query) |
            Q(instructor__last_name__icontains=search_query)
        )
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    
    # Filter by level
    level = request.GET.get('level')
    if level:
        courses = courses.filter(level=level)
    
    # Filter by price
    price_filter = request.GET.get('price')
    if price_filter == 'free':
        courses = courses.filter(is_free=True)
    elif price_filter == 'paid':
        courses = courses.filter(is_free=False)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'popular':
        courses = courses.order_by('-total_enrollments')
    elif sort_by == 'rating':
        courses = courses.order_by('-average_rating')
    elif sort_by == 'price_low':
        courses = courses.order_by('price')
    elif sort_by == 'price_high':
        courses = courses.order_by('-price')
    else:
        courses = courses.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_level': level,
        'selected_price': price_filter,
        'sort_by': sort_by,
    }
    
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    """
    Course detail page
    """
    course = get_object_or_404(
        Course.objects.select_related('category', 'instructor'),
        slug=slug,
        status='published'
    )
    
    # Get lessons
    lessons = course.lessons.all()
    
    # Get reviews
    reviews = course.reviews.select_related('user').order_by('-created_at')[:10]
    
    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            is_enrolled = True
        except Enrollment.DoesNotExist:
            pass
    
    # Check if user has already reviewed
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(user=request.user, course=course).exists()

    # Check if user has an enrollment request for this course
    enrollment_request = None
    if request.user.is_authenticated:
        try:
            from .models import EnrollmentRequest
            enrollment_request = EnrollmentRequest.objects.filter(user=request.user, course=course).first()
        except Exception:
            enrollment_request = None
    
    context = {
        'course': course,
        'lessons': lessons,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'user_has_reviewed': user_has_reviewed,
        'enrollment_request': enrollment_request,
    }
    
    return render(request, 'courses/course_detail.html', context)


@login_required
def lesson_detail(request, course_slug, lesson_slug):
    """
    Individual lesson view (only for enrolled students)
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    
    # Check enrollment or preview access
    enrollment = None
    if not lesson.is_preview:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course, is_active=True)
        except Enrollment.DoesNotExist:
            messages.error(request, 'You need to enroll in this course to access this lesson.')
            return redirect('courses:course_detail', slug=course_slug)
    
    # Get all lessons for navigation
    lessons = course.lessons.all()
    # Prepare list for index-based navigation
    lessons_list = list(lessons)
    prev_lesson = None
    next_lesson = None
    try:
        current_index = next(i for i, l in enumerate(lessons_list) if l.id == lesson.id)
        if current_index > 0:
            prev_lesson = lessons_list[current_index - 1]
        if current_index < len(lessons_list) - 1:
            next_lesson = lessons_list[current_index + 1]
    except StopIteration:
        prev_lesson = None
        next_lesson = None
    
    # Get lesson materials
    materials = lesson.materials.all()
    
    # Mark lesson as viewed/completed if enrolled
    if enrollment:
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
    
    # Precompute completed lesson ids for template membership checks
    completed_lesson_ids = []
    if enrollment:
        completed_lesson_ids = list(
            enrollment.lesson_progress.filter(is_completed=True).values_list('lesson_id', flat=True)
        )
    
    context = {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
        'materials': materials,
        'enrollment': enrollment,
        'completed_lesson_ids': completed_lesson_ids,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    }
    
    # If user is authenticated, include enrollment request status for this course
    if request.user.is_authenticated:
        try:
            from .models import EnrollmentRequest
            context['enrollment_request'] = EnrollmentRequest.objects.filter(user=request.user, course=course).first()
        except Exception:
            context['enrollment_request'] = None
    
    return render(request, 'courses/lesson_detail.html', context)


@login_required
def mark_lesson_complete(request, course_slug, lesson_slug):
    """
    Mark a lesson as complete
    """
    if request.method == 'POST':
        course = get_object_or_404(Course, slug=course_slug)
        lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
        
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course, is_active=True)
            lesson_progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
            
            if not lesson_progress.is_completed:
                lesson_progress.is_completed = True
                from django.utils import timezone
                lesson_progress.completed_at = timezone.now()
                lesson_progress.save()
                
                # Update enrollment progress
                total_lessons = course.lessons.count()
                completed_lessons = LessonProgress.objects.filter(
                    enrollment=enrollment,
                    is_completed=True
                ).count()
                
                enrollment.progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
                enrollment.save()
                
                messages.success(request, f'Lesson "{lesson.title}" marked as complete!')
            
        except Enrollment.DoesNotExist:
            messages.error(request, 'You are not enrolled in this course.')
    
    return redirect('courses:lesson_detail', course_slug=course_slug, lesson_slug=lesson_slug)


@login_required
def add_review(request, slug):
    """
    Add or update a course review
    """
    if request.method == 'POST':
        course = get_object_or_404(Course, slug=slug)
        
        # Check if user is enrolled
        if not Enrollment.objects.filter(user=request.user, course=course).exists():
            messages.error(request, 'You must be enrolled in the course to leave a review.')
            return redirect('courses:course_detail', slug=slug)
        
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if not rating:
            messages.error(request, 'Please select a rating.')
            return redirect('courses:course_detail', slug=slug)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Invalid rating value.')
            return redirect('courses:course_detail', slug=slug)
        
        # Create or update review
        review, created = Review.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={'rating': rating, 'comment': comment}
        )
        
        # Update course average rating
        avg_rating = Review.objects.filter(course=course).aggregate(Avg('rating'))['rating__avg']
        course.average_rating = avg_rating or 0
        course.save()
        
        if created:
            messages.success(request, 'Thank you for your review!')
        else:
            messages.success(request, 'Your review has been updated!')
    
    return redirect('courses:course_detail', slug=slug)


def category_detail(request, slug):
    """
    Courses in a specific category
    """
    category = get_object_or_404(Category, slug=slug)
    courses = Course.objects.filter(
        category=category,
        status='published'
    ).select_related('instructor')
    
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'courses/category_detail.html', context)


@login_required
@student_required
def request_enrollment(request, slug):
    """
    Student requests free enrollment in a paid course
    """
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=slug)
    
    # Check if already requested
    from .models import EnrollmentRequest
    existing_request = EnrollmentRequest.objects.filter(
        user=request.user,
        course=course
    ).first()
    
    if existing_request:
        if existing_request.status == 'pending':
            messages.info(request, 'You already have a pending enrollment request for this course.')
        elif existing_request.status == 'rejected':
            messages.warning(request, 'Your previous enrollment request was rejected.')
        return redirect('courses:course_detail', slug=slug)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        
        if not reason:
            messages.error(request, 'Please provide a reason for your enrollment request.')
        else:
            # Create enrollment request
            EnrollmentRequest.objects.create(
                user=request.user,
                course=course,
                reason=reason
            )
            messages.success(
                request,
                'Your enrollment request has been submitted! An admin will review it soon.'
            )
            return redirect('courses:course_detail', slug=slug)
    
    context = {
        'course': course,
    }
    
    return render(request, 'courses/request_enrollment.html', context)


@login_required
def my_enrollment_requests(request):
    """
    View user's enrollment requests
    """
    from .models import EnrollmentRequest
    
    requests = EnrollmentRequest.objects.filter(
        user=request.user
    ).select_related('course').order_by('-created_at')
    
    context = {
        'enrollment_requests': requests,
    }
    
    return render(request, 'courses/my_enrollment_requests.html', context)
