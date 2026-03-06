"""
Custom decorators for role-based access control
"""
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator for views that require admin access
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('users:login')
        
        if request.user.user_type != 'admin' and not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('courses:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def instructor_required(view_func):
    """
    Decorator for views that require instructor access
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('users:login')
        
        if request.user.user_type not in ['instructor', 'admin'] and not request.user.is_superuser:
            messages.error(request, 'Only instructors can access this page.')
            return redirect('courses:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """
    Decorator for views that require student access
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('users:login')
        
        if request.user.user_type != 'student':
            messages.error(request, 'This page is only for students.')
            return redirect('courses:home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """
    Generic decorator that accepts multiple roles
    Usage: @role_required('admin', 'instructor')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('users:login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if request.user.user_type not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('courses:home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
