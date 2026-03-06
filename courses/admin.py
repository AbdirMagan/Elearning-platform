from django.contrib import admin
from .models import (
    Category, Course, Lesson, Material, Quiz, Question, Answer,
    Enrollment, LessonProgress, QuizAttempt, Review, EnrollmentRequest
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order', 'is_preview', 'video_duration']


class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 0
    fields = ['title', 'passing_score', 'max_attempts']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'price', 'status', 'total_enrollments', 'average_rating', 'created_at']
    list_filter = ['status', 'level', 'category', 'is_featured', 'is_free']
    search_fields = ['title', 'description', 'instructor__email']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['total_enrollments', 'average_rating', 'created_at', 'updated_at']
    inlines = [LessonInline, QuizInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'instructor', 'category')
        }),
        ('Media', {
            'fields': ('thumbnail', 'promo_video')
        }),
        ('Course Details', {
            'fields': ('level', 'language', 'duration_hours', 'requirements', 'what_you_will_learn')
        }),
        ('Pricing', {
            'fields': ('price', 'is_free', 'discount_price')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('total_enrollments', 'average_rating', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.instructor_id:
            obj.instructor = request.user
        super().save_model(request, obj, form, change)


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'video_duration', 'is_preview', 'created_at']
    list_filter = ['course', 'is_preview']
    search_fields = ['title', 'course__title']
    inlines = [MaterialInline]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'file_type', 'file_size', 'created_at']
    list_filter = ['file_type']
    search_fields = ['title', 'lesson__title']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'passing_score', 'time_limit', 'max_attempts']
    list_filter = ['course']
    search_fields = ['title', 'course__title']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_type', 'points', 'order']
    list_filter = ['question_type', 'quiz']
    inlines = [AnswerInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'progress_percentage', 'is_active', 'enrolled_at', 'certificate_issued']
    list_filter = ['is_active', 'certificate_issued', 'enrolled_at']
    search_fields = ['user__email', 'course__title']
    readonly_fields = ['enrolled_at', 'completed_at']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'is_completed', 'completed_at', 'time_spent']
    list_filter = ['is_completed']
    search_fields = ['enrollment__user__email', 'lesson__title']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'quiz', 'score', 'passed', 'attempt_number', 'started_at']
    list_filter = ['passed', 'started_at']
    search_fields = ['enrollment__user__email', 'quiz__title']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__email', 'course__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for enrollment requests
    """
    list_display = ['user', 'course', 'status', 'created_at', 'processed_by', 'processed_at']
    list_filter = ['status', 'created_at', 'processed_at']
    search_fields = ['user__email', 'user__username', 'course__title', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'course', 'reason', 'status')
        }),
        ('Admin Response', {
            'fields': ('admin_notes', 'processed_by', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and obj.status in ['approved', 'rejected'] and not obj.processed_by:
            obj.processed_by = request.user
            if obj.status == 'approved':
                obj.approve(request.user, obj.admin_notes or '')
                return
            elif obj.status == 'rejected':
                obj.reject(request.user, obj.admin_notes or '')
                return
        super().save_model(request, obj, form, change)
# Add these imports at top
from .models import (
    Category, Course, Lesson, Material, Quiz, Question, Answer,
    Enrollment, LessonProgress, QuizAttempt, Review, EnrollmentRequest,
    HeroSlide, Announcement  # Add these
)

# Add at the end of file:

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'gradient_color', 'created_at']
    list_filter = ['is_active', 'gradient_color']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'subtitle']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'background_image')
        }),
        ('Styling', {
            'fields': ('gradient_color',)
        }),
        ('Buttons', {
            'fields': ('button_text', 'button_url', 'show_secondary_button')
        }),
        ('Display', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'announcement_type', 'is_active', 'show_on_homepage', 'show_on_all_pages', 'priority', 'created_at']
    list_filter = ['announcement_type', 'is_active', 'show_on_homepage', 'show_on_all_pages']
    list_editable = ['is_active', 'priority']
    search_fields = ['title', 'message']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'message', 'announcement_type')
        }),
        ('Action Link', {
            'fields': ('link_text', 'link_url'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('is_active', 'show_on_homepage', 'show_on_all_pages', 'is_dismissible', 'priority')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
    )