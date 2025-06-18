import unittest
import asyncio
from unittest.mock import patch, AsyncMock
from payos import PayOS
from payos.type import PaymentData, CreatePaymentResult, PaymentLinkInformation
from payos.custom_error import PayOSError

class TestPayOS(unittest.TestCase):
    def setUp(self):
        """Set up test data and PayOS instance"""
        self.client_id = "test_client_id"
        self.api_key = "test_api_key"
        self.checksum_key = "test_checksum_key"
        self.payos = PayOS(
            client_id=self.client_id,
            api_key=self.api_key,
            checksum_key=self.checksum_key
        )
        self.payment_data = PaymentData(
            orderCode=12345,
            amount=1000000,
            description="Test payment",
            cancelUrl="https://example.com/cancel",
            returnUrl="https://example.com/return"
        )

    def test_init_valid(self):
        """Test PayOS initialization with valid data"""
        payos = PayOS(self.client_id, self.api_key, self.checksum_key)
        self.assertIsInstance(payos, PayOS)

    def test_init_invalid_types(self):
        """Test PayOS initialization with invalid data types"""
        with self.assertRaises(TypeError):
            PayOS(123, self.api_key, self.checksum_key)  # invalid client_id type
        with self.assertRaises(TypeError):
            PayOS(self.client_id, 123, self.checksum_key)  # invalid api_key type
        with self.assertRaises(TypeError):
            PayOS(self.client_id, self.api_key, 123)  # invalid checksum_key type

    @patch('aiohttp.ClientSession.post')
    async def test_create_payment_link_success(self, mock_post):
        """Test successful payment link creation"""
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "code": "00",
            "desc": "Success",
            "data": {
                "bin": "970422",
                "accountNumber": "12345678",
                "accountName": "Test Account",
                "amount": 1000000,
                "description": "Test payment",
                "orderCode": 12345,
                "currency": "VND",
                "paymentLinkId": "abc123",
                "status": "PENDING",
                "checkoutUrl": "https://example.com/checkout",
                "qrCode": "qr_data_here"
            },
            "signature": "valid_signature"
        }
        mock_post.return_value = mock_response

        result = await self.payos.createPaymentLink(self.payment_data)
        self.assertIsInstance(result, CreatePaymentResult)
        self.assertEqual(result.orderCode, self.payment_data.orderCode)
        self.assertEqual(result.amount, self.payment_data.amount)

    @patch('aiohttp.ClientSession.post')
    async def test_create_payment_link_failure(self, mock_post):
        """Test payment link creation failure"""
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "code": "01",
            "desc": "Error occurred",
            "data": None
        }
        mock_post.return_value = mock_response

        with self.assertRaises(PayOSError) as context:
            await self.payos.createPaymentLink(self.payment_data)
        self.assertEqual(context.exception.code, "01")

    @patch('aiohttp.ClientSession.get')
    async def test_get_payment_link_information_success(self, mock_get):
        """Test successful retrieval of payment link information"""
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "code": "00",
            "desc": "Success",
            "data": {
                "paymentLinkId": "abc123",
                "orderCode": 12345,
                "amount": 1000000,
                "status": "PAID",
                "transactions": []
            },
            "signature": "valid_signature"
        }
        mock_get.return_value = mock_response

        result = await self.payos.getPaymentLinkInformation("12345")
        self.assertIsInstance(result, PaymentLinkInformation)
        self.assertEqual(result.orderCode, 12345)

    def test_get_payment_link_information_invalid_order_id(self):
        """Test get payment link information with invalid order ID type"""
        with self.assertRaises(ValueError):
            asyncio.run(self.payos.getPaymentLinkInformation(None))

if __name__ == "__main__":
    unittest.main()
