"""
Sifalo Pay Payment Gateway Integration
https://developer.sifalopay.com
"""
import requests
import json
import logging
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)


class SifaloPayService:
    """
    Service class for Sifalo Pay payment integration
    """
    
    # Base URLs
    SANDBOX_URL = "https://sandbox.sifalopay.com/api/v1"
    PRODUCTION_URL = "https://api.sifalopay.com/api/v1"
    
    def __init__(self):
        # Use getattr to avoid AttributeError if a setting is missing
        self.api_key = getattr(settings, 'SIFALO_API_KEY', '')
        self.merchant_id = getattr(settings, 'SIFALO_MERCHANT_ID', '')
        self.username = getattr(settings, 'SIFALO_USERNAME', '')
        self.password = getattr(settings, 'SIFALO_PASSWORD', '')
        self.mode = getattr(settings, 'SIFALO_MODE', 'sandbox')  # 'sandbox' or 'production'
        self.callback_url = getattr(settings, 'SIFALO_CALLBACK_URL', '')

        # If merchant id not provided, fall back to username when available
        if not self.merchant_id and self.username:
            self.merchant_id = self.username
        
        # Set base URL based on mode
        if self.mode == 'production':
            self.base_url = self.PRODUCTION_URL
        else:
            self.base_url = self.SANDBOX_URL
    
    def get_headers(self):
        """Get request headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        return headers

    def _get_auth(self):
        """Return requests auth tuple when using username/password fallback, else None"""
        if not self.api_key and self.username and self.password:
            return (self.username, self.password)
        return None
    
    def initialize_payment(self, transaction_id, amount, phone_number, description=''):
        """
        Initialize a payment transaction
        
        Args:
            transaction_id: Unique transaction identifier
            amount: Payment amount (Decimal)
            phone_number: Customer phone number
            description: Payment description
            
        Returns:
            dict: Response from Sifalo Pay API
        """
        # Use Sifalo Checkout gateway endpoint as per docs
        url = f"{self.base_url}/gateway/"

        # return_url must include order_id as query param per docs
        return_url = f"{settings.SITE_URL}/payments/status/{transaction_id}/?order_id={transaction_id}"

        payload = {
            'amount': str(float(amount)),
            'gateway': 'checkout',
            'currency': 'USD',  # or 'SOS' for Somali Shilling
            'return_url': return_url,
            'description': description,
            'order_id': str(transaction_id),
        }
        
        try:
            logger.info(f"Initiating Sifalo Pay payment: {payload}")
            
            response = requests.post(
                url,
                headers=self.get_headers(),
                json=payload,
                timeout=30,
                auth=self._get_auth()
            )

            response_data = response.json()
            
            logger.info(f"Sifalo Pay response: {response_data}")
            
            # For Checkout API, successful response contains 'key' and 'token'
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Sifalo Pay API error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to payment gateway'
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            return {
                'success': False,
                'error': 'Invalid response from payment gateway',
                'message': 'Failed to process payment response'
            }
    
    def verify_payment(self, transaction_id):
        """
        Verify payment status
        
        Args:
            transaction_id: Transaction identifier to verify
            
        Returns:
            dict: Payment verification response
        """
        # Use Checkout verify endpoint per docs
        url = f"{self.base_url}/gateway/verify.php"

        payload = {'sid': transaction_id}

        try:
            logger.info(f"Verifying payment: {transaction_id}")

            response = requests.post(
                url,
                headers=self.get_headers(),
                json=payload,
                timeout=30,
                auth=self._get_auth()
            )

            response_data = response.json()

            logger.info(f"Verification response: {response_data}")

            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment verification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_callback(self, callback_data):
        """
        Process callback from Sifalo Pay
        
        Args:
            callback_data: Data received from callback
            
        Returns:
            dict: Processed callback information
        """
        try:
            # Extract relevant data
            transaction_id = callback_data.get('transaction_id')
            status = callback_data.get('status')
            amount = callback_data.get('amount')
            phone_number = callback_data.get('phone_number')
            reference = callback_data.get('reference')
            
            logger.info(f"Processing callback for transaction: {transaction_id}")
            
            result = {
                'transaction_id': transaction_id,
                'status': status,
                'amount': Decimal(str(amount)) if amount else None,
                'phone_number': phone_number,
                'reference': reference,
                'success': status == 'completed' or status == 'success',
                'raw_data': callback_data
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Callback processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_refund(self, transaction_id, amount, reason=''):
        """
        Process a refund
        
        Args:
            transaction_id: Original transaction ID
            amount: Refund amount
            reason: Refund reason
            
        Returns:
            dict: Refund response
        """
        url = f"{self.base_url}/refunds/create"
        
        payload = {
            'merchant_id': self.merchant_id,
            'transaction_id': str(transaction_id),
            'amount': float(amount),
            'reason': reason
        }
        
        try:
            logger.info(f"Processing refund: {payload}")
            
            response = requests.post(
                url,
                headers=self.get_headers(),
                json=payload,
                timeout=30,
                auth=self._get_auth()
            )
            
            response_data = response.json()
            
            logger.info(f"Refund response: {response_data}")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Refund error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_transaction_status(self, transaction_id):
        """
        Get current transaction status
        
        Args:
            transaction_id: Transaction to check
            
        Returns:
            str: Transaction status
        """
        response = self.verify_payment(transaction_id)
        
        if response.get('success'):
            return response.get('status', 'unknown')
        
        return 'unknown'
    
    @staticmethod
    def parse_status(sifalo_status):
        """
        Parse Sifalo Pay status to our internal status
        
        Args:
            sifalo_status: Status from Sifalo Pay
            
        Returns:
            str: Internal status ('completed', 'failed', 'processing', 'pending')
        """
        status_map = {
            'completed': 'completed',
            'success': 'completed',
            'successful': 'completed',
            'paid': 'completed',
            'failed': 'failed',
            'error': 'failed',
            'declined': 'failed',
            'cancelled': 'failed',
            'processing': 'processing',
            'pending': 'pending',
            'initiated': 'pending',
        }
        
        return status_map.get(str(sifalo_status).lower(), 'pending')


# Sifalo Pay Response Codes
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


def get_response_message(code):
    """Get human-readable message for response code"""
    return SIFALO_RESPONSE_CODES.get(str(code), 'Unknown error')
