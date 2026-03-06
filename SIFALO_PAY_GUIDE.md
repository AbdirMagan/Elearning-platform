# 💳 Sifalo Pay Integration Guide

Complete guide for integrating Sifalo Pay payment gateway.

## Overview

Sifalo Pay is now the primary payment gateway for the E-Learning Platform, replacing WaafiPay.

## Getting Started

### Step 1: Get Sifalo Pay Account

1. Visit: https://business.sifalopay.com
2. Sign up for a merchant account
3. Complete verification
4. Get your API credentials

### Step 2: Get API Credentials

From your Sifalo Pay Business Dashboard:

1. Go to **Settings** → **API Keys**
2. Copy your credentials:
   - API Key
   - Merchant ID

### Step 3: Configure Application

Update your `.env` file:

```bash
# Sifalo Pay Configuration
SIFALO_API_KEY=your_actual_api_key_here
SIFALO_MERCHANT_ID=your_merchant_id_here
SIFALO_MODE=sandbox  # Use 'production' when ready
SIFALO_CALLBACK_URL=http://localhost:8000/payments/callback/
```

**For Production:**
```bash
SIFALO_MODE=production
SIFALO_CALLBACK_URL=https://yourdomain.com/payments/callback/
```

## API Integration

### Payment Flow

```
1. Student clicks "Buy Course"
2. Enter phone number
3. System calls Sifalo Pay API
4. Customer receives payment prompt
5. Customer enters PIN
6. Sifalo Pay sends callback
7. System creates enrollment
8. Student gets access
```

### Initialize Payment

```python
from payments.sifalopay import SifaloPayService

service = SifaloPayService()
response = service.initialize_payment(
    transaction_id='unique-id-123',
    amount=49.99,
    phone_number='+252612345678',
    description='Course: Python Programming'
)
```

### Response Format

```python
{
    'success': True,
    'reference': 'SFP123456',
    'status': 'processing',
    'message': 'Payment initiated'
}
```

### Verify Payment

```python
verification = service.verify_payment('unique-id-123')

if verification.get('success'):
    status = verification.get('status')
    # Status: 'completed', 'failed', 'processing', 'pending'
```

### Handle Callback

Callbacks are automatically handled at: `/payments/callback/`

```python
@csrf_exempt
def sifalo_callback(request):
    # Automatically processes callback
    # Creates enrollment on success
    # Updates transaction status
    pass
```

## Testing

### Sandbox Mode

```bash
SIFALO_MODE=sandbox
```

**Test Credentials:**
- Use your sandbox API key
- Test phone numbers work normally
- No real money charged

**Test Flow:**
1. Create test course with price
2. Register as student
3. Attempt purchase
4. Use test phone number
5. Complete mock payment
6. Verify enrollment created

### Production Mode

```bash
SIFALO_MODE=production
```

⚠️ **Important:**
- Use production API key
- Real money will be charged
- Test with small amounts first
- Monitor transactions closely

## Database Schema

### Transaction Model

```python
Transaction:
- transaction_id (UUID)
- user (FK)
- course (FK)
- amount (Decimal)
- payment_method ('sifalo')
- status ('pending', 'processing', 'completed', 'failed')
- phone_number
- sifalo_reference
- sifalo_response (JSON)
- created_at
- completed_at
```

### Run Migrations

```powershell
python manage.py makemigrations payments
python manage.py migrate
```

## API Endpoints

### Your Application

```
POST /payments/checkout/<slug>/          # Checkout page
POST /payments/initiate/<slug>/          # Initiate payment
GET  /payments/status/<transaction_id>/  # Check status
POST /payments/callback/                 # Sifalo callback (webhook)
GET  /payments/history/                  # Transaction history
```

### Sifalo Pay API

```
POST /api/v1/payments/initiate           # Start payment
GET  /api/v1/payments/verify/<id>        # Check status
POST /api/v1/refunds/create              # Process refund
```

## Error Handling

### Response Codes

```python
SIFALO_RESPONSE_CODES = {
    '00': 'Success',
    '01': 'Insufficient Balance',
    '02': 'Invalid Account',
    '03': 'Invalid Amount',
    '04': 'Transaction Failed',
    '05': 'Duplicate Transaction',
    '06': 'Invalid Phone Number',
    '07': 'Transaction Timeout',
    '08': 'System Error',
    '09': 'Invalid Merchant',
    '10': 'Permission Denied',
}
```

### Handle Errors

```python
response = service.initialize_payment(...)

if not response.get('success'):
    error_message = response.get('message', 'Unknown error')
    # Show error to user
    # Log for debugging
```

## Security

### API Key Protection

✅ **Do:**
- Store in .env file
- Never commit to Git
- Use environment variables
- Rotate keys regularly

❌ **Don't:**
- Hardcode in code
- Share publicly
- Commit to repository
- Log in plain text

### Callback Security

```python
# Verify callback signature (if Sifalo provides)
def verify_callback(data, signature):
    # Implement signature verification
    pass
```

### SSL/HTTPS

⚠️ **Production Requirements:**
- HTTPS required for callbacks
- SSL certificate installed
- Secure webhook endpoint

## Monitoring

### Track Transactions

```python
# In Django shell
from payments.models import Transaction

# Today's transactions
today = Transaction.objects.filter(
    created_at__date=timezone.now().date()
)

# Success rate
total = Transaction.objects.count()
completed = Transaction.objects.filter(status='completed').count()
rate = (completed / total * 100) if total > 0 else 0

print(f"Success rate: {rate:.1f}%")
```

### Failed Payments

```python
failed = Transaction.objects.filter(
    status='failed'
).order_by('-created_at')

for trans in failed[:10]:
    print(f"{trans.user.email}: {trans.description}")
```

## Troubleshooting

### Payment Not Initiating

**Check:**
1. API key correct in .env
2. Merchant ID correct
3. Phone number format valid
4. Amount is positive
5. Network connectivity

**Debug:**
```python
python manage.py shell

from payments.sifalopay import SifaloPayService
service = SifaloPayService()

# Test connection
response = service.initialize_payment(
    transaction_id='test-123',
    amount=1.00,
    phone_number='+252612345678',
    description='Test'
)

print(response)
```

### Callback Not Received

**Check:**
1. Callback URL accessible
2. HTTPS in production
3. Firewall not blocking
4. Correct URL in settings
5. Server running

**Test Callback:**
```bash
# Simulate callback
curl -X POST http://localhost:8000/payments/callback/ \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"test-123","status":"completed"}'
```

### Status Not Updating

**Check:**
1. Callback handler working
2. Transaction ID matches
3. Database migrations applied
4. No errors in logs

**Manual Update:**
```python
from payments.models import Transaction

trans = Transaction.objects.get(transaction_id='xxx')
trans.status = 'completed'
trans.save()
```

## Best Practices

### 1. Idempotency

Use unique transaction IDs:
```python
import uuid
transaction_id = uuid.uuid4()
```

### 2. Logging

Log all API interactions:
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Payment initiated: {transaction_id}")
logger.error(f"Payment failed: {error}")
```

### 3. Retry Logic

Handle temporary failures:
```python
from time import sleep

max_retries = 3
for attempt in range(max_retries):
    response = service.verify_payment(trans_id)
    if response.get('success'):
        break
    sleep(2 ** attempt)  # Exponential backoff
```

### 4. User Communication

Keep users informed:
- Show clear payment status
- Send email confirmations
- Provide transaction receipts
- Enable support contact

## Migration from WaafiPay

### Data Migration

WaafiPay transactions are preserved:

```python
# Old transactions remain in database
Transaction.objects.filter(payment_method='waafi')

# New transactions use Sifalo
Transaction.objects.filter(payment_method='sifalo')
```

### Configuration

Both can coexist:
```bash
# Sifalo Pay (new)
SIFALO_API_KEY=...
SIFALO_MERCHANT_ID=...

# WaafiPay (legacy)
WAAFIPAY_API_KEY=...
WAAFIPAY_MERCHANT_ID=...
```

## Support

### Sifalo Pay Support

- Website: https://sifalopay.com
- Developer Docs: https://developer.sifalopay.com
- Business Dashboard: https://business.sifalopay.com
- Email: support@sifalopay.com

### Integration Issues

1. Check documentation
2. Review API response
3. Test in sandbox
4. Contact Sifalo support
5. Check server logs

## Checklist

**Before Going Live:**

- [ ] Production API key obtained
- [ ] Merchant account verified
- [ ] SSL certificate installed
- [ ] Callback URL accessible via HTTPS
- [ ] Test transactions successful
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Backup plan ready
- [ ] Support contact available

## Quick Reference

### .env Configuration
```bash
SIFALO_API_KEY=your_key
SIFALO_MERCHANT_ID=your_id
SIFALO_MODE=sandbox
SIFALO_CALLBACK_URL=http://localhost:8000/payments/callback/
```

### Common Commands
```bash
# Run migrations
python manage.py migrate

# Test in shell
python manage.py shell

# View logs
tail -f logs/payment.log

# Check transactions
python manage.py shell
>>> from payments.models import Transaction
>>> Transaction.objects.all()
```

### Important URLs
```
Sandbox: https://sandbox.sifalopay.com/api/v1
Production: https://api.sifalopay.com/api/v1
Dashboard: https://business.sifalopay.com
```

---

**Your Sifalo Pay integration is ready!** 💳✅
