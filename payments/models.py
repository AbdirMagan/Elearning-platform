from django.db import models
from django.conf import settings
from courses.models import Course
import uuid


class Transaction(models.Model):
    """
    Payment transaction model for WaafiPay payments
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    # Transaction identification
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reference_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Payment details
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # WaafiPay specific fields
    waafipay_transaction_id = models.CharField(max_length=200, blank=True, null=True)
    waafipay_status = models.CharField(max_length=50, blank=True, null=True)
    waafipay_response = models.JSONField(blank=True, null=True)
    
    # Sifalo Pay specific fields
    sifalo_reference = models.CharField(max_length=100, blank=True, null=True)
    sifalo_response = models.JSONField(blank=True, null=True)
    
    # Payment method
    payment_method = models.CharField(max_length=50, default='WaafiPay')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Additional information
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.user.email} - ${self.amount}"
    
    def is_successful(self):
        """Check if transaction was successful"""
        return self.status == 'completed'
    
    def mark_as_completed(self):
        """Mark transaction as completed"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, reason=''):
        """Mark transaction as failed"""
        self.status = 'failed'
        if reason:
            self.description = f"{self.description}\nFailure reason: {reason}"
        self.save()


class PaymentMethod(models.Model):
    """
    Store user's payment methods (optional)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.phone_number}"
    
    def save(self, *args, **kwargs):
        # If this is set as default, remove default from other payment methods
        if self.is_default:
            PaymentMethod.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Refund(models.Model):
    """
    Refund requests and processing
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    )
    
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='refund')
    
    reason = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund for {self.transaction.transaction_id} - ${self.amount}"
