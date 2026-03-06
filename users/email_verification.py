"""
Email verification system for user account activation
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string


class EmailVerification(models.Model):
    """
    Model to store email verification codes
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verification'
    )
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
    
    def __str__(self):
        return f"{self.user.email} - {'Verified' if self.is_verified else 'Pending'}"
    
    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_code():
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Check if verification code is expired"""
        return timezone.now() > self.expires_at
    
    def regenerate_code(self):
        """Generate a new verification code"""
        self.verification_code = self.generate_code()
        self.expires_at = timezone.now() + timedelta(hours=24)
        self.attempts = 0
        self.save()
