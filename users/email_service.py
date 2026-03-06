"""
Email service for sending verification codes and notifications
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_verification_email(user, verification_code):
    """
    Send verification code to user's email
    """
    subject = 'Verify Your Email - E-Learning Platform'
    
    message = f"""
    Hi {user.get_full_name() or user.username},
    
    Thank you for registering on our E-Learning Platform!
    
    Your verification code is: {verification_code}
    
    This code will expire in 24 hours.
    
    Please enter this code on the verification page to activate your account.
    
    If you didn't create an account, please ignore this email.
    
    Best regards,
    E-Learning Team
    """
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #4f46e5; text-align: center;">Welcome to E-Learning Platform!</h2>
            
            <p>Hi <strong>{user.get_full_name() or user.username}</strong>,</p>
            
            <p>Thank you for registering on our platform. To complete your registration, please verify your email address.</p>
            
            <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #666;">Your Verification Code:</p>
                <h1 style="margin: 10px 0; color: #4f46e5; font-size: 36px; letter-spacing: 5px;">{verification_code}</h1>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                <strong>Note:</strong> This code will expire in 24 hours.
            </p>
            
            <p>If you didn't create an account, please ignore this email.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="text-align: center; color: #666; font-size: 12px;">
                &copy; 2024 E-Learning Platform. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@elearning.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_welcome_email(user):
    """
    Send welcome email after successful verification
    """
    subject = 'Welcome to E-Learning Platform!'
    
    message = f"""
    Hi {user.get_full_name() or user.username},
    
    Your email has been successfully verified!
    
    You can now:
    - Browse our courses
    - Enroll in courses
    - Track your progress
    - Access premium content
    
    Start your learning journey today!
    
    Visit: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}
    
    Best regards,
    E-Learning Team
    """
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #10b981; text-align: center;">🎉 Welcome to E-Learning Platform!</h2>
            
            <p>Hi <strong>{user.get_full_name() or user.username}</strong>,</p>
            
            <p>Your email has been successfully verified! 🎓</p>
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px; margin: 20px 0;">
                <h3 style="color: white; margin: 0;">You Can Now:</h3>
                <ul style="color: white; text-align: left; display: inline-block;">
                    <li>Browse our extensive course library</li>
                    <li>Enroll in courses that interest you</li>
                    <li>Track your learning progress</li>
                    <li>Access premium content</li>
                    <li>Connect with instructors</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}" 
                   style="background-color: #4f46e5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Start Learning Now
                </a>
            </div>
            
            <p>If you have any questions, feel free to contact our support team.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="text-align: center; color: #666; font-size: 12px;">
                &copy; 2024 E-Learning Platform. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@elearning.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def resend_verification_code(user, new_code):
    """
    Resend verification code to user
    """
    subject = 'New Verification Code - E-Learning Platform'
    
    message = f"""
    Hi {user.get_full_name() or user.username},
    
    You requested a new verification code.
    
    Your new verification code is: {new_code}
    
    This code will expire in 24 hours.
    
    Best regards,
    E-Learning Team
    """
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #4f46e5; text-align: center;">New Verification Code</h2>
            
            <p>Hi <strong>{user.get_full_name() or user.username}</strong>,</p>
            
            <p>You requested a new verification code. Here it is:</p>
            
            <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                <h1 style="margin: 0; color: #4f46e5; font-size: 36px; letter-spacing: 5px;">{new_code}</h1>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                <strong>Note:</strong> This code will expire in 24 hours.
            </p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="text-align: center; color: #666; font-size: 12px;">
                &copy; 2024 E-Learning Platform. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@elearning.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"New verification code sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to resend verification code to {user.email}: {str(e)}")
        return False


def send_enrollment_request_notification(user, course, status, admin_notes=''):
    """
    Send notification to student when their enrollment request is processed.
    status: 'approved' or 'rejected'
    """
    subject = f"Your enrollment request for '{course.title}' has been {status.capitalize()}"

    if status == 'approved':
        message = f"Hi {user.get_full_name() or user.username},\n\nYour enrollment request for the course '{course.title}' has been approved. You can now access the course: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/courses/course/{course.slug}/\n\nBest regards,\nE-Learning Team"
        html_message = f"<p>Hi <strong>{user.get_full_name() or user.username}</strong>,</p><p>Your enrollment request for the course '<strong>{course.title}</strong>' has been <strong>approved</strong>. You can now access the course <a href=\"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/courses/course/{course.slug}/\">here</a>.</p><p>Best regards,<br>E-Learning Team</p>"
    else:
        message = f"Hi {user.get_full_name() or user.username},\n\nWe reviewed your enrollment request for '{course.title}' and unfortunately it was rejected.\n\nAdmin notes: {admin_notes}\n\nYou can still purchase the course here: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/courses/course/{course.slug}/\n\nBest regards,\nE-Learning Team"
        html_message = f"<p>Hi <strong>{user.get_full_name() or user.username}</strong>,</p><p>We reviewed your enrollment request for '<strong>{course.title}</strong>' and unfortunately it was <strong>rejected</strong>.</p><p><strong>Admin notes:</strong> {admin_notes}</p><p>You can still purchase the course <a href=\"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/courses/course/{course.slug}/\">here</a>.</p><p>Best regards,<br>E-Learning Team</p>"

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@elearning.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Enrollment request notification sent to {user.email} (status={status})")
        return True
    except Exception as e:
        logger.error(f"Failed to send enrollment notification to {user.email}: {str(e)}")
        return False
