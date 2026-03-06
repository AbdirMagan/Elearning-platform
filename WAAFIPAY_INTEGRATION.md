# WaafiPay Integration Guide

Complete guide for integrating WaafiPay payment gateway into the e-learning platform.

## Overview

WaafiPay is a mobile money and payment gateway service. This integration allows students to purchase courses using their mobile wallets.

## Setup

### 1. Get WaafiPay Credentials

1. Visit [WaafiPay Dashboard](https://dashboard.waafipay.com)
2. Sign up or log in
3. Navigate to **API Settings**
4. Copy your credentials:
   - Merchant UID
   - API User ID
   - API Key

### 2. Configure Environment Variables

Add to `.env`:
```
WAAFIPAY_MERCHANT_ID=your_merchant_id
WAAFIPAY_API_USER_ID=your_api_user_id
WAAFIPAY_API_KEY=your_api_key
WAAFIPAY_MODE=sandbox  # or 'production'
WAAFIPAY_CALLBACK_URL=http://localhost:8000/payments/callback/
```

### 3. Test in Sandbox Mode

Before going live, test in sandbox mode:
- Use test phone numbers provided by WaafiPay
- Test different payment scenarios
- Verify callbacks are working

## Payment Flow

### 1. Initialize Payment

When a user clicks "Buy Now":
```python
# views.py
transaction_obj = Transaction.objects.create(
    user=request.user,
    course=course,
    amount=amount,
    phone_number=phone_number
)

response = waafipay_service.initialize_payment(
    transaction_id=transaction_obj.transaction_id,
    amount=amount,
    phone_number=phone_number,
    description=f'Course: {course.title}'
)
```

### 2. User Receives Payment Request

- User receives a push notification on their phone
- User enters PIN to confirm payment
- Payment is processed

### 3. Callback Handling

WaafiPay sends a callback to your server:
```python
# Callback URL: /payments/callback/
@csrf_exempt
def waafipay_callback(request):
    callback_data = json.loads(request.body)
    parsed_data = waafipay_service.parse_callback_response(callback_data)
    
    if parsed_data['success']:
        # Complete enrollment
        transaction_obj.mark_as_completed()
        Enrollment.objects.create(user=user, course=course)
```

### 4. Payment Verification

Optionally verify payment status:
```python
response = waafipay_service.verify_payment(transaction_id)
if response.get('responseCode') == '2001':
    # Payment successful
```

## API Reference

### Initialize Payment

**Endpoint**: `POST /api/v1/payments`

**Request**:
```json
{
  "schemaVersion": "1.0",
  "requestId": "unique-transaction-id",
  "timestamp": "2024-01-01T12:00:00",
  "channelName": "WEB",
  "serviceName": "API_PURCHASE",
  "serviceParams": {
    "merchantUid": "your_merchant_id",
    "apiUserId": "your_api_user_id",
    "apiKey": "your_api_key",
    "paymentMethod": "MWALLET_ACCOUNT",
    "payerInfo": {
      "accountNo": "+252611234567"
    },
    "transactionInfo": {
      "referenceId": "unique-reference",
      "invoiceId": "invoice-123",
      "amount": 50.00,
      "currency": "USD",
      "description": "Course Purchase"
    }
  }
}
```

**Success Response**:
```json
{
  "responseCode": "2001",
  "responseMsg": "Success",
  "params": {
    "transactionId": "waafipay-tx-id",
    "referenceId": "your-reference-id",
    "state": "APPROVED",
    "amount": 50.00
  }
}
```

### Verify Payment

**Endpoint**: `POST /api/v1/payments/verify`

**Request**:
```json
{
  "schemaVersion": "1.0",
  "requestId": "unique-request-id",
  "timestamp": "2024-01-01T12:00:00",
  "channelName": "WEB",
  "serviceName": "API_QUERY",
  "serviceParams": {
    "merchantUid": "your_merchant_id",
    "apiUserId": "your_api_user_id",
    "apiKey": "your_api_key",
    "transactionId": "transaction-to-verify"
  }
}
```

## Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 2001 | Success | Transaction approved |
| 4001 | Failed | Insufficient balance |
| 4002 | Failed | Invalid account |
| 4003 | Failed | Transaction declined |
| 4004 | Failed | System error |
| 5001 | Error | Invalid request |

## Error Handling

### Common Errors

**1. Connection Error**
```python
try:
    response = waafipay_service.initialize_payment(...)
except WaafiPayError as e:
    logger.error(f"WaafiPay error: {str(e)}")
    # Show user-friendly error
```

**2. Invalid Phone Number**
```python
if not phone_number.startswith('+252'):
    messages.error(request, 'Please enter a valid phone number')
```

**3. Insufficient Balance**
```python
if response.get('responseCode') == '4001':
    messages.error(request, 'Insufficient balance. Please top up your account.')
```

## Testing

### Test Phone Numbers (Sandbox)

WaafiPay provides test phone numbers for sandbox testing:
- Success: `+252612345678`
- Insufficient Balance: `+252612345679`
- Invalid Account: `+252612345680`

### Test Scenarios

1. **Successful Payment**
   ```python
   # Use test phone number
   # Complete payment flow
   # Verify enrollment created
   # Check transaction status
   ```

2. **Failed Payment**
   ```python
   # Use insufficient balance number
   # Verify error handling
   # Check transaction marked as failed
   ```

3. **Callback Test**
   ```bash
   # Send test callback
   curl -X POST http://localhost:8000/payments/callback/ \
     -H "Content-Type: application/json" \
     -d @test_callback.json
   ```

## Security Best Practices

1. **Never expose credentials**
   - Store in environment variables
   - Never commit to version control

2. **Validate callback data**
   ```python
   # Verify callback signature if available
   # Check transaction exists
   # Validate amount matches
   ```

3. **Use HTTPS in production**
   ```python
   if not DEBUG:
       SECURE_SSL_REDIRECT = True
   ```

4. **Implement rate limiting**
   ```python
   from django.core.cache import cache
   
   # Limit payment attempts
   key = f'payment_attempts_{user.id}'
   attempts = cache.get(key, 0)
   if attempts > 5:
       return error_response
   ```

## Monitoring

### Log Payment Events

```python
import logging
logger = logging.getLogger('payments')

# Log all payment attempts
logger.info(f'Payment initiated: {transaction_id}')
logger.info(f'Payment completed: {transaction_id}')
logger.error(f'Payment failed: {transaction_id} - {error}')
```

### Dashboard Metrics

Monitor in Django admin:
- Total transactions
- Success rate
- Failed transactions
- Average transaction amount
- Revenue by day/week/month

## Troubleshooting

### Payment Not Completing

1. Check callback URL is accessible
2. Verify credentials are correct
3. Check transaction logs
4. Test in sandbox first

### Callback Not Received

1. Ensure callback URL is publicly accessible
2. Check firewall settings
3. Verify CSRF exemption on callback endpoint
4. Test with ngrok for local development

### Double Enrollment

```python
# Use get_or_create to prevent duplicates
enrollment, created = Enrollment.objects.get_or_create(
    user=user,
    course=course
)
```

## Production Checklist

- [ ] Switch to production credentials
- [ ] Update callback URL to production domain
- [ ] Enable HTTPS
- [ ] Test complete payment flow
- [ ] Set up monitoring and alerts
- [ ] Configure backup payment method
- [ ] Document payment support process
- [ ] Train support team

## Support

### WaafiPay Support
- Email: support@waafipay.com
- Documentation: https://docs.waafipay.com
- Dashboard: https://dashboard.waafipay.com

### Integration Issues
- Check logs first
- Review this documentation
- Contact support with transaction ID
- Provide relevant error messages

## Additional Resources

- [WaafiPay Official Documentation](https://docs.waafipay.com)
- [Python SDK](https://github.com/waafipay/sdk-python)
- [API Reference](https://docs.waafipay.com/api-reference)
- [Postman Collection](https://www.postman.com/waafipay/workspace/waafipay)
