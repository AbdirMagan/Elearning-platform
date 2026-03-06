"""
Custom permission classes for role-based access control
"""
from django.core.exceptions import PermissionDenied


class RolePermissionMixin:
    """
    Mixin for checking user roles and permissions
    """
    
    @staticmethod
    def is_admin(user):
        """Check if user is admin"""
        return user.is_authenticated and (user.user_type == 'admin' or user.is_superuser)
    
    @staticmethod
    def is_instructor(user):
        """Check if user is instructor"""
        return user.is_authenticated and user.user_type == 'instructor'
    
    @staticmethod
    def is_student(user):
        """Check if user is student"""
        return user.is_authenticated and user.user_type == 'student'
    
    @staticmethod
    def can_manage_all(user):
        """Check if user can manage everything (admin only)"""
        return user.is_authenticated and (user.user_type == 'admin' or user.is_superuser)
    
    @staticmethod
    def can_create_course(user):
        """Check if user can create courses (instructor or admin)"""
        return user.is_authenticated and user.user_type in ['instructor', 'admin'] or user.is_superuser
    
    @staticmethod
    def can_edit_course(user, course):
        """Check if user can edit a specific course"""
        if not user.is_authenticated:
            return False
        
        # Admin can edit any course
        if user.user_type == 'admin' or user.is_superuser:
            return True
        
        # Instructor can only edit their own courses
        if user.user_type == 'instructor':
            return course.instructor == user
        
        return False
    
    @staticmethod
    def can_delete_course(user, course):
        """Check if user can delete a specific course"""
        if not user.is_authenticated:
            return False
        
        # Only admin can delete courses
        if user.user_type == 'admin' or user.is_superuser:
            return True
        
        return False
    
    @staticmethod
    def can_view_students(user, course):
        """Check if user can view students enrolled in a course"""
        if not user.is_authenticated:
            return False
        
        # Admin can view all students
        if user.user_type == 'admin' or user.is_superuser:
            return True
        
        # Instructor can view students in their courses
        if user.user_type == 'instructor':
            return course.instructor == user
        
        return False
    
    @staticmethod
    def can_enroll(user):
        """Check if user can enroll in courses (students only)"""
        return user.is_authenticated and user.user_type == 'student'
    
    @staticmethod
    def can_approve_course(user):
        """Check if user can approve/publish courses (admin only)"""
        return user.is_authenticated and (user.user_type == 'admin' or user.is_superuser)


class PermissionManager:
    """
    Centralized permission management
    """
    
    # Administrator permissions
    ADMIN_PERMISSIONS = [
        'view_all_courses',
        'create_course',
        'edit_any_course',
        'delete_any_course',
        'approve_course',
        'view_all_students',
        'view_all_transactions',
        'manage_users',
        'manage_categories',
        'process_refunds',
    ]
    
    # Instructor permissions
    INSTRUCTOR_PERMISSIONS = [
        'create_course',
        'edit_own_course',
        'view_own_students',
        'view_own_transactions',
        'create_lessons',
        'create_quizzes',
    ]
    
    # Student permissions
    STUDENT_PERMISSIONS = [
        'enroll_course',
        'view_enrolled_courses',
        'submit_reviews',
        'request_refund',
        'access_lessons',
        'take_quizzes',
    ]
    
    @classmethod
    def get_user_permissions(cls, user):
        """Get all permissions for a user based on their role"""
        if not user.is_authenticated:
            return []
        
        if user.user_type == 'admin' or user.is_superuser:
            return cls.ADMIN_PERMISSIONS
        elif user.user_type == 'instructor':
            return cls.INSTRUCTOR_PERMISSIONS
        elif user.user_type == 'student':
            return cls.STUDENT_PERMISSIONS
        
        return []
    
    @classmethod
    def has_permission(cls, user, permission):
        """Check if user has a specific permission"""
        user_permissions = cls.get_user_permissions(user)
        return permission in user_permissions
