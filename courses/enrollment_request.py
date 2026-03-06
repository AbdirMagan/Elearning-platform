"""
Course enrollment request system
"""
from django.db import models
from django.conf import settings
from courses.models import Course


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
        from courses.models import Enrollment
        
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
