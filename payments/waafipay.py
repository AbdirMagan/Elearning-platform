"""
WaafiPay Integration Service

This module handles all WaafiPay API interactions for payment processing.
Documentation: https://docs.waafipay.com/quickstart
"""

import requests
import json
import logging
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)


class WaafiPayError(Exception):
    """Custom exception for WaafiPay errors"""
    pass


class WaafiPayService:
    """
    Service class for WaafiPay API integration
    """
    
    def __init__(self):
        self.merchant_id = settings.WAAFIPAY_MERCHANT_ID
        self.api_user_id = settings.WAAFIPAY_API_USER_ID
        self.api_key = settings.WAAFIPAY_API_KEY
        self.mode = settings.WAAFIPAY_MODE  # 'sandbox' or 'production'
        
        # API endpoints
        if self.mode == 'production':
            self.base_url = 'https://api.waafipay.net'
        else:
            self.base_url = 'https://sandbox.waafipay.net'
        
        self.headers = {
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, endpoint, method='POST', data=None):
        """
        Make HTTP request to WaafiPay API
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=self.headers, timeout=30)
            elif method == 'GET':
                response = requests.get(url, params=data, headers=self.headers, timeout=30)
            else:
                raise WaafiPayError(f"Unsupported HTTP method: {method}")
            
            # Log the request and response
            logger.info(f"WaafiPay Request: {method} {url}")
            logger.info(f"WaafiPay Response Status: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"WaafiPay API Error: {str(e)}")
            raise WaafiPayError(f"API request failed: {str(e)}")
    
    def initialize_payment(self, transaction_id, amount, phone_number, description='Course Purchase'):
        """
        Initialize a payment with WaafiPay
        
        Args:
            transaction_id: Unique transaction identifier
            amount: Payment amount
            phone_number: Customer phone number
            description: Payment description
        
        Returns:
            dict: WaafiPay API response
        """
        payload = {
            'schemaVersion': '1.0',
            'requestId': str(transaction_id),
            'timestamp': self._get_timestamp(),
            'channelName': 'WEB',
            'serviceName': 'API_PURCHASE',
            'serviceParams': {
                'merchantUid': self.merchant_id,
                'apiUserId': self.api_user_id,
                'apiKey': self.api_key,
                'paymentMethod': 'MWALLET_ACCOUNT',
                'payerInfo': {
                    'accountNo': phone_number
                },
                'transactionInfo': {
                    'referenceId': str(transaction_id),
                    'invoiceId': str(transaction_id),
                    'amount': float(amount),
                    'currency': 'USD',
                    'description': description
                }
            }
        }
        
        logger.info(f"Initializing payment for transaction {transaction_id}")
        response = self._make_request('/api/v1/payments', method='POST', data=payload)
        
        return response
    
    def verify_payment(self, transaction_id):
        """
        Verify payment status with WaafiPay
        
        Args:
            transaction_id: Transaction ID to verify
        
        Returns:
            dict: Payment verification response
        """
        payload = {
            'schemaVersion': '1.0',
            'requestId': str(transaction_id),
            'timestamp': self._get_timestamp(),
            'channelName': 'WEB',
            'serviceName': 'API_QUERY',
            'serviceParams': {
                'merchantUid': self.merchant_id,
                'apiUserId': self.api_user_id,
                'apiKey': self.api_key,
                'transactionId': str(transaction_id)
            }
        }
        
        logger.info(f"Verifying payment for transaction {transaction_id}")
        response = self._make_request('/api/v1/payments/verify', method='POST', data=payload)
        
        return response
    
    def process_refund(self, transaction_id, amount, reason=''):
        """
        Process a refund through WaafiPay
        
        Args:
            transaction_id: Original transaction ID
            amount: Refund amount
            reason: Reason for refund
        
        Returns:
            dict: Refund response
        """
        payload = {
            'schemaVersion': '1.0',
            'requestId': f"{transaction_id}_refund",
            'timestamp': self._get_timestamp(),
            'channelName': 'WEB',
            'serviceName': 'API_REFUND',
            'serviceParams': {
                'merchantUid': self.merchant_id,
                'apiUserId': self.api_user_id,
                'apiKey': self.api_key,
                'transactionId': str(transaction_id),
                'amount': float(amount),
                'description': reason or 'Refund processed'
            }
        }
        
        logger.info(f"Processing refund for transaction {transaction_id}")
        response = self._make_request('/api/v1/refunds', method='POST', data=payload)
        
        return response
    
    def _get_timestamp(self):
        """
        Get current timestamp in WaafiPay format
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    @staticmethod
    def parse_callback_response(callback_data):
        """
        Parse callback data from WaafiPay
        
        Args:
            callback_data: JSON data from WaafiPay callback
        
        Returns:
            dict: Parsed callback data
        """
        try:
            if isinstance(callback_data, str):
                callback_data = json.loads(callback_data)
            
            return {
                'success': callback_data.get('responseCode') == '2001',
                'transaction_id': callback_data.get('params', {}).get('referenceId'),
                'waafipay_transaction_id': callback_data.get('params', {}).get('transactionId'),
                'amount': callback_data.get('params', {}).get('amount'),
                'status': callback_data.get('responseMsg'),
                'full_response': callback_data
            }
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Error parsing WaafiPay callback: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'full_response': callback_data
            }


# Initialize the service
waafipay_service = WaafiPayService()
