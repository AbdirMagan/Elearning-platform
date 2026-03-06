from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db import transaction as db_transaction
from django.utils import timezone
from .models import Transaction, Refund
from .sifalopay import SifaloPayService
from courses.models import Course, Enrollment
import logging
import json
import uuid

logger = logging.getLogger(__name__)


@login_required
def checkout(request, course_slug):
    """
    Checkout page for course purchase
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    
    # Check if already enrolled
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
    }
    
    return render(request, 'payments/checkout.html', context)


@login_required
def initiate_payment(request, course_slug):
    """
    Initiate payment with Sifalo Pay
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course_slug)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        
        if not phone_number:
            messages.error(request, 'Please provide your phone number.')
            return redirect('payments:checkout', course_slug=course_slug)
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=request.user,
            course=course,
            amount=course.get_effective_price(),
            payment_method='sifalo',
            status='pending',
            phone_number=phone_number,
        )
        
        # Initialize Sifalo Pay payment
        sifalo_service = SifaloPayService()
        response = sifalo_service.initialize_payment(
            transaction_id=transaction.transaction_id,
            amount=transaction.amount,
            phone_number=phone_number,
            description=f"Course: {course.title}"
        )
        
        # Save Sifalo response
        transaction.sifalo_response = response
        transaction.save()
        
        if response.get('success'):
            transaction.status = 'processing'
            transaction.sifalo_reference = response.get('reference')
            transaction.save()
            
            messages.success(
                request,
                'Payment initiated! Please check your phone to complete the payment.'
            )
            return redirect('payments:payment_status', transaction_id=transaction.transaction_id)
        else:
            transaction.status = 'failed'
            transaction.description = response.get('message', 'Payment initiation failed')
            transaction.save()
            
            messages.error(
                request,
                f"Payment failed: {response.get('message', 'Unknown error')}"
            )
            return redirect('payments:checkout', course_slug=course_slug)
    
    return redirect('payments:checkout', course_slug=course_slug)


def payment_status(request, transaction_id):
    """
    Check and display payment status
    """
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    
    # Verify payment status with Sifalo Pay
    if transaction.status == 'processing':
        sifalo_service = SifaloPayService()
        verification = sifalo_service.verify_payment(transaction.transaction_id)
        
        if verification.get('success'):
            status = verification.get('status')
            internal_status = SifaloPayService.parse_status(status)
            
            if internal_status == 'completed' and transaction.status != 'completed':
                # Payment successful - create enrollment
                transaction.status = 'completed'
                transaction.completed_at = timezone.now()
                transaction.sifalo_response = verification
                transaction.save()
                
                # Create enrollment
                enrollment, created = Enrollment.objects.get_or_create(
                    user=transaction.user,
                    course=transaction.course
                )
                
                if created:
                    transaction.course.total_enrollments += 1
                    transaction.course.save()
                
                messages.success(request, 'Payment completed successfully! You now have access to the course.')
            
            elif internal_status == 'failed':
                transaction.status = 'failed'
                transaction.description = verification.get('message', 'Payment failed')
                transaction.save()
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'payments/payment_status.html', context)


@csrf_exempt
def sifalo_callback(request):
    """
    Handle callback from Sifalo Pay
    """
    if request.method == 'POST':
        try:
            # Parse callback data
            if request.content_type == 'application/json':
                callback_data = json.loads(request.body)
            else:
                callback_data = request.POST.dict()
            
            logger.info(f"Sifalo Pay callback received: {callback_data}")
            
            # Process callback
            sifalo_service = SifaloPayService()
            result = sifalo_service.process_callback(callback_data)
            
            transaction_id = result.get('transaction_id')
            
            if transaction_id:
                try:
                    transaction = Transaction.objects.get(transaction_id=transaction_id)
                    
                    # Update transaction
                    if result.get('success'):
                        transaction.status = 'completed'
                        transaction.completed_at = timezone.now()
                        transaction.sifalo_reference = result.get('reference')
                        transaction.sifalo_response = callback_data
                        transaction.save()
                        
                        # Create enrollment
                        enrollment, created = Enrollment.objects.get_or_create(
                            user=transaction.user,
                            course=transaction.course
                        )
                        
                        if created:
                            transaction.course.total_enrollments += 1
                            transaction.course.save()
                        
                        logger.info(f"Payment completed for transaction: {transaction_id}")
                        
                        return JsonResponse({'status': 'success', 'message': 'Payment processed'})
                    else:
                        transaction.status = 'failed'
                        transaction.description = result.get('error', 'Payment failed')
                        transaction.sifalo_response = callback_data
                        transaction.save()
                        
                        logger.error(f"Payment failed for transaction: {transaction_id}")
                        
                        return JsonResponse({'status': 'failed', 'message': 'Payment failed'})
                
                except Transaction.DoesNotExist:
                    logger.error(f"Transaction not found: {transaction_id}")
                    return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)
            
            return JsonResponse({'status': 'error', 'message': 'Invalid callback data'}, status=400)
        
        except Exception as e:
            logger.error(f"Callback processing error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return HttpResponse('Method not allowed', status=405)


@login_required
def transaction_history(request):
    """
    View user's transaction history
    """
    transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('course').order_by('-created_at')
    
    context = {
        'transactions': transactions,
    }
    
    return render(request, 'payments/transaction_history.html', context)


@login_required
def request_refund(request, transaction_id):
    """
    Request a refund for a transaction
    """
    transaction = get_object_or_404(
        Transaction,
        transaction_id=transaction_id,
        user=request.user,
        status='completed'
    )
    
    # Check if refund already requested
    if Refund.objects.filter(transaction=transaction).exists():
        messages.info(request, 'Refund already requested for this transaction.')
        return redirect('payments:transaction_history')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        
        if not reason:
            messages.error(request, 'Please provide a reason for the refund.')
        else:
            # Create refund request
            refund = Refund.objects.create(
                transaction=transaction,
                amount=transaction.amount,
                reason=reason,
                status='pending'
            )
            
            messages.success(
                request,
                'Refund request submitted successfully. We will review it shortly.'
            )
            return redirect('payments:transaction_history')
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'payments/request_refund.html', context)
