from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, EmailVerification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin interface for CustomUser model
    """
    list_display = ['email', 'username', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'bio', 'profile_picture', 'date_of_birth', 'is_verified')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'user_type', 'first_name', 'last_name')
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for Profile model
    """
    list_display = ['user', 'country', 'city', 'email_notifications', 'created_at']
    list_filter = ['email_notifications', 'course_updates', 'created_at']
    search_fields = ['user__email', 'user__username', 'country', 'city']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Email Verification
    """
    list_display = ['user', 'verification_code', 'is_verified', 'attempts', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__email', 'user__username', 'verification_code']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False
