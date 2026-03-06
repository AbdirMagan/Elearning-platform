from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Category(models.Model):
    """
    Course categories for organization
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Font Awesome icon class')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """
    Main Course model
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'user_type': 'instructor'}
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    
    # Media
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    promo_video = models.FileField(upload_to='courses/promo_videos/', blank=True, null=True)
    
    # Course Details
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    language = models.CharField(max_length=50, default='English')
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_free = models.BooleanField(default=False)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    # Requirements & Outcomes
    requirements = models.TextField(blank=True, help_text='What students need before starting')
    what_you_will_learn = models.TextField(blank=True)
    
    # Status & Visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Statistics
    total_enrollments = models.IntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_free:
            self.price = 0
        super().save(*args, **kwargs)
    
    def get_effective_price(self):
        """Return the effective price considering discounts"""
        if self.is_free:
            return 0
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price


class Lesson(models.Model):
    """
    Individual lessons within a course
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Content - Offline video files
    video_file = models.FileField(
        upload_to='courses/videos/',
        blank=True,
        null=True,
        help_text='Upload video file (MP4, WebM, OGG recommended)'
    )
    video_duration = models.IntegerField(default=0, help_text='Duration in minutes')
    
    # Optional: Still support YouTube as alternative
    youtube_url = models.URLField(
        blank=True,
        null=True,
        help_text='YouTube video URL (alternative to video file)'
    )
    youtube_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='YouTube video ID (extracted automatically)'
    )
    
    # Ordering
    order = models.IntegerField(default=0)
    
    # Visibility
    is_preview = models.BooleanField(
        default=False,
        help_text='Allow non-enrolled users to preview this lesson'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Extract YouTube ID from URL if provided
        if self.youtube_url and not self.youtube_id:
            self.youtube_id = self.extract_youtube_id(self.youtube_url)
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def extract_youtube_id(url):
        """Extract YouTube video ID from URL"""
        import re
        
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_youtube_embed_url(self):
        """Get YouTube embed URL"""
        if self.youtube_id:
            return f"https://www.youtube.com/embed/{self.youtube_id}"
        return None
    
    def has_video(self):
        """Check if lesson has any video content"""
        return bool(self.video_file or self.youtube_id)


class Material(models.Model):
    """
    Downloadable materials for lessons
    """
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='courses/materials/')
    file_type = models.CharField(max_length=10, blank=True)
    file_size = models.IntegerField(default=0, help_text='Size in bytes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class Quiz(models.Model):
    """
    Quizzes for courses
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Settings
    passing_score = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    time_limit = models.IntegerField(default=30, help_text='Time limit in minutes')
    max_attempts = models.IntegerField(default=3)
    
    # Ordering
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Quizzes'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    """
    Questions for quizzes
    """
    QUESTION_TYPES = (
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
        ('true_false', 'True/False'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single')
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class Answer(models.Model):
    """
    Answer choices for questions
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question} - {self.answer_text[:50]}"


class Enrollment(models.Model):
    """
    Student enrollment in courses
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    # Enrollment details
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Progress tracking
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    certificate_issued = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"


class LessonProgress(models.Model):
    """
    Track user progress on individual lessons
    """
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_spent = models.IntegerField(default=0, help_text='Time spent in seconds')
    
    class Meta:
        unique_together = ['enrollment', 'lesson']
        verbose_name_plural = 'Lesson Progress'
    
    def __str__(self):
        return f"{self.enrollment.user.email} - {self.lesson.title}"


class QuizAttempt(models.Model):
    """
    Track user quiz attempts
    """
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    passed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.enrollment.user.email} - {self.quiz.title} (Attempt {self.attempt_number})"


class Review(models.Model):
    """
    Course reviews and ratings
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['course', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.rating}★)"


class EnrollmentRequest(models.Model):
    """
    Model for users to request free enrollment in paid courses
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollment_requests'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollment_requests'
    )
    reason = models.TextField(help_text='Why do you want to enroll in this course?')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin response
    admin_notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_requests'
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-created_at']
        verbose_name = 'Enrollment Request'
        verbose_name_plural = 'Enrollment Requests'
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.status})"
    
    def approve(self, admin_user, notes=''):
        """Approve enrollment request"""
        from django.utils import timezone
        
        self.status = 'approved'
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        self.admin_notes = notes
        self.save()
        
        # Create enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            user=self.user,
            course=self.course
        )
        
        if created:
            self.course.total_enrollments += 1
            self.course.save()
        
        return enrollment
    
    def reject(self, admin_user, notes=''):
        """Reject enrollment request"""
        from django.utils import timezone
        
        self.status = 'rejected'
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        self.admin_notes = notes
        self.save()
# Add these imports at the top if not already there
from django.core.validators import MinValueValidator, MaxValueValidator

# Add at the end of the file:

class HeroSlide(models.Model):
    """
    Model for hero carousel slides - Admin can manage
    """
    title = models.CharField(max_length=200, help_text='Main heading (e.g., "Learn Without Limits")')
    subtitle = models.TextField(help_text='Subtitle or description')
    
    # Background image
    background_image = models.ImageField(
        upload_to='hero_slides/',
        help_text='Recommended size: 1920x800px'
    )
    
    # Styling
    GRADIENT_CHOICES = (
        ('none', 'No Gradient (Image Only)'),
        ('purple', 'Purple'),
        ('green', 'Green'),
        ('orange', 'Orange'),
        ('blue', 'Blue'),
        ('red', 'Red'),
    )
    gradient_color = models.CharField(max_length=20, choices=GRADIENT_CHOICES, default='purple')
    
    # Call to action
    button_text = models.CharField(max_length=50, default='Explore Courses')
    button_url = models.CharField(max_length=200, default='/courses/')
    
    show_secondary_button = models.BooleanField(default=True, help_text='Show "Get Started" button')
    
    # Display settings
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text='Display order (0, 1, 2...)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Hero Slide'
        verbose_name_plural = 'Hero Slides'
    
    def __str__(self):
        return f"{self.title} (Order: {self.order})"
    
    def get_gradient_style(self):
        """Get CSS gradient"""
        gradients = {
            'none':'none',
            'purple': 'linear-gradient(135deg, rgba(79, 70, 229, 0.9), rgba(124, 58, 237, 0.9))',
            'green': 'linear-gradient(135deg, rgba(16, 185, 129, 0.9), rgba(5, 150, 105, 0.9))',
            'orange': 'linear-gradient(135deg, rgba(245, 158, 11, 0.9), rgba(217, 119, 6, 0.9))',
            'blue': 'linear-gradient(135deg, rgba(59, 130, 246, 0.9), rgba(37, 99, 235, 0.9))',
            'red': 'linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.9))',
        }
        return gradients.get(self.gradient_color, gradients['purple'])


class Announcement(models.Model):
    """
    Model for announcements and discount messages
    """
    ANNOUNCEMENT_TYPE_CHOICES = (
        ('info', 'Information'),
        ('success', 'Success/Promotion'),
        ('warning', 'Warning'),
        ('danger', 'Important'),
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPE_CHOICES, default='info')
    
    # Link (optional)
    link_text = models.CharField(max_length=50, blank=True, help_text='e.g., "View Offer"')
    link_url = models.CharField(max_length=200, blank=True)
    
    # Display settings
    is_active = models.BooleanField(default=True)
    show_on_homepage = models.BooleanField(default=True)
    show_on_all_pages = models.BooleanField(default=False, help_text='Show as top banner on all pages')
    
    # Scheduling
    start_date = models.DateTimeField(blank=True, null=True, help_text='Leave empty for immediate')
    end_date = models.DateTimeField(blank=True, null=True, help_text='Leave empty for no end')
    
    priority = models.IntegerField(default=0, help_text='Higher = appears first')
    is_dismissible = models.BooleanField(default=True, help_text='Can users close it?')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.title
    
    def is_currently_active(self):
        """Check if should be shown now"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def get_bootstrap_class(self):
        """Get Bootstrap alert class"""
        return {
            'info': 'alert-info',
            'success': 'alert-success',
            'warning': 'alert-warning',
            'danger': 'alert-danger',
        }.get(self.announcement_type, 'alert-info')