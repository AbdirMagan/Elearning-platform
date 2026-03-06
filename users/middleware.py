"""
Single Device Login Middleware
Prevents users from logging in from multiple devices simultaneously
"""
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone


class SingleDeviceLoginMiddleware:
    """
    Middleware to enforce single device login per user
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Ensure AuthenticationMiddleware has run and `user` exists
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get current session key
            current_session_key = request.session.session_key
            
            # Check if user has a stored session key
            stored_session_key = request.user.profile.session_key if hasattr(request.user, 'profile') else None
            
            # If there's a different session, logout from current
            if stored_session_key and stored_session_key != current_session_key:
                # Check if stored session is still active
                try:
                    stored_session = Session.objects.get(session_key=stored_session_key)
                    if stored_session.expire_date > timezone.now():
                        # Another session is active, logout this one
                        messages.warning(
                            request,
                            'Your account is being used on another device. You have been logged out from this device.'
                        )
                        logout(request)
                        return redirect('users:login')
                except Session.DoesNotExist:
                    # Old session doesn't exist, update to current
                    if hasattr(request.user, 'profile'):
                        request.user.profile.session_key = current_session_key
                        request.user.profile.save()
            elif not stored_session_key:
                # First login, store session key
                if hasattr(request.user, 'profile'):
                    request.user.profile.session_key = current_session_key
                    request.user.profile.save()
        
        response = self.get_response(request)
        return response
