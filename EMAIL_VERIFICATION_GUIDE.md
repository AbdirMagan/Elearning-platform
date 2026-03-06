# 📧 Email Verification Setup Guide

Complete guide to setting up email verification for user registration.

## Overview

Email verification is now **required** for all new user registrations. Users receive a 6-digit verification code via email that must be entered to activate their account.

## Features

✅ **6-digit verification codes**  
✅ **24-hour expiration**  
✅ **5 attempt limit**  
✅ **Code resending**  
✅ **Welcome email after verification**  
✅ **Beautiful HTML email templates**  
✅ **Console fallback for development**  

## Email Flow

1. User registers → Account created (inactive)
2. System generates 6-digit code
3. Verification email sent
4. User enters code
5. Account activated
6. Welcome email sent

## Email Configuration

### For Development (Console Backend)

No setup needed! Emails print to console.

**In .env:**
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Check console/terminal** for verification codes when testing.

### For Production (Gmail)

#### Step 1: Get Gmail App Password

1. Go to Google Account Settings
2. Security → 2-Step Verification (enable if not already)
3. App passwords → Select app: Mail → Generate
4. Copy the 16-character password

#### Step 2: Configure .env

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=noreply@yoursite.com
SITE_URL=https://yoursite.com
```

### For Other Email Providers

#### Outlook/Hotmail

```bash
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
```

#### Yahoo

```bash
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yahoo.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### SendGrid (Recommended for Production)

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yoursite.com
```

#### Mailgun

```bash
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@yourdomain.com
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=noreply@yoursite.com
```

## Testing Email Verification

### Development Testing

```powershell
# Start server
python manage.py runserver

# Register new user
# Go to: http://127.0.0.1:8000/users/register/
# Fill form and submit

# Check terminal/console for verification code
# It will look like:
-------------------------------------------------------------------------------
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Verify Your Email - E-Learning Platform
From: noreply@elearning.com
To: user@example.com

Your verification code is: 123456
-------------------------------------------------------------------------------

# Copy code and paste in verification page
```

### Production Testing

1. Register with real email
2. Check inbox (and spam folder!)
3. Enter 6-digit code
4. Verify account activated
5. Check for welcome email

## Database Schema

### EmailVerification Model

```python
EmailVerification:
- user (OneToOne)
- verification_code (6 digits)
- created_at
- expires_at (24 hours)
- is_verified (boolean)
- attempts (max 5)
```

### Run Migration

```powershell
python manage.py makemigrations users
python manage.py migrate
```

## User Flow

### Registration

```
1. User fills registration form
2. System creates user (is_active=False)
3. System generates 6-digit code
4. Email sent with code
5. User redirected to verification page
```

### Verification

```
1. User enters 6-digit code
2. System validates code
3. If correct:
   - Mark user as verified
   - Activate account (is_active=True)
   - Send welcome email
   - Redirect to login
4. If incorrect:
   - Increment attempt counter
   - Show remaining attempts
   - Allow retry (max 5 attempts)
```

### Resending Code

```
1. User clicks "Resend Code"
2. System generates new code
3. Reset attempt counter
4. Extend expiration to 24 hours
5. Send new email
```

## Admin Panel

Manage email verifications in Django admin:

```
Admin → Users → Email Verifications

You can see:
- Verification status
- Codes (for support)
- Attempt counts
- Expiration times
```

## Customization

### Change Code Length

Edit `users/models.py`:

```python
def generate_code():
    return ''.join(random.choices(string.digits, k=8))  # 8 digits
```

### Change Expiration Time

Edit `users/models.py`:

```python
self.expires_at = timezone.now() + timedelta(hours=48)  # 48 hours
```

### Change Attempt Limit

Edit `users/views.py`:

```python
elif verification.attempts >= 10:  # 10 attempts
```

### Customize Email Templates

Edit `users/email_service.py` to modify:
- Email subject
- Email body (HTML)
- Styling
- Content

## Troubleshooting

### Emails Not Sending

**Check:**
1. EMAIL_BACKEND in .env
2. Email credentials correct
3. App password (not regular password) for Gmail
4. Port 587 not blocked by firewall
5. Check Django logs for errors

**Test email configuration:**
```python
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test message.',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

### Code Not Working

**Check:**
1. Code not expired (24 hours)
2. Attempts not exceeded (5 max)
3. Code entered correctly (6 digits)
4. Database has EmailVerification record

**Reset verification:**
```python
python manage.py shell

from users.models import CustomUser, EmailVerification

user = CustomUser.objects.get(email='user@example.com')
verification = user.email_verification
verification.regenerate_code()
print(f"New code: {verification.verification_code}")
```

### User Stuck at Verification

**Manually verify user:**
```python
python manage.py shell

from users.models import CustomUser

user = CustomUser.objects.get(email='user@example.com')
user.is_active = True
user.is_verified = True
user.save()

verification = user.email_verification
verification.is_verified = True
verification.save()
```

## Security Features

✅ **Rate limiting** - 5 attempts max  
✅ **Time expiration** - 24 hours  
✅ **Unique codes** - Random generation  
✅ **Inactive accounts** - Until verified  
✅ **No password reset** - Until verified  

## Best Practices

### Development
- Use console backend
- Test with real email occasionally
- Check spam folder

### Production
- Use professional email service (SendGrid, Mailgun)
- Monitor email delivery rates
- Set up SPF/DKIM records
- Use your domain email (not Gmail)
- Monitor verification success rates

### Email Deliverability

1. **SPF Record** - Add to DNS
   ```
   v=spf1 include:_spf.google.com ~all
   ```

2. **DKIM** - Configure with email provider

3. **DMARC** - Add to DNS
   ```
   v=DMARC1; p=none; rua=mailto:admin@yourdomain.com
   ```

4. **Reverse DNS** - Configure with hosting provider

## Support Scenarios

### User Never Received Email

1. Check spam folder
2. Verify email address correct
3. Resend code
4. Check email logs
5. Manually verify if urgent

### Code Expired

1. User clicks "Resend Code"
2. New code generated
3. New email sent

### Too Many Attempts

1. User clicks "Resend Code"
2. Attempts reset to 0
3. New code generated

## Monitoring

### Track Verification Rates

```python
# In Django shell
from users.models import EmailVerification

total = EmailVerification.objects.count()
verified = EmailVerification.objects.filter(is_verified=True).count()
rate = (verified / total * 100) if total > 0 else 0

print(f"Verification rate: {rate:.1f}%")
```

### Find Unverified Users

```python
from users.models import CustomUser

unverified = CustomUser.objects.filter(is_active=False, is_verified=False)
print(f"Unverified users: {unverified.count()}")
```

## Production Checklist

- [ ] Email provider configured (SendGrid, Mailgun, etc.)
- [ ] SPF/DKIM records set
- [ ] Default from email set
- [ ] Site URL configured
- [ ] Email templates tested
- [ ] Spam folder checked
- [ ] Verification flow tested end-to-end
- [ ] Expiration tested
- [ ] Attempt limit tested
- [ ] Resend functionality tested
- [ ] Welcome email tested

## Resources

- Django Email Documentation: https://docs.djangoproject.com/en/5.0/topics/email/
- SendGrid: https://sendgrid.com/
- Mailgun: https://www.mailgun.com/
- Gmail App Passwords: https://support.google.com/accounts/answer/185833

---

**Your email verification system is ready!** 📧✅
