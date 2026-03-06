from django.contrib import admin
from .models import Transaction, PaymentMethod, Refund


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'course', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'reference_number', 'user__email', 'course__title', 'phone_number']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at', 'completed_at', 'waafipay_response']
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('transaction_id', 'reference_number', 'user', 'course')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'payment_method', 'phone_number', 'status')
        }),
        ('WaafiPay Info', {
            'fields': ('waafipay_transaction_id', 'waafipay_status', 'waafipay_response')
        }),
        ('Additional Info', {
            'fields': ('description', 'ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of transactions
        return False


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'is_default', 'is_active', 'created_at']
    list_filter = ['is_default', 'is_active', 'created_at']
    search_fields = ['user__email', 'phone_number']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'amount', 'status', 'created_at', 'processed_by']
    list_filter = ['status', 'created_at']
    search_fields = ['transaction__transaction_id', 'transaction__user__email', 'reason']
    readonly_fields = ['transaction', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Refund Info', {
            'fields': ('transaction', 'amount', 'status', 'reason')
        }),
        ('Processing', {
            'fields': ('admin_notes', 'processed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.processed_by:
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)
