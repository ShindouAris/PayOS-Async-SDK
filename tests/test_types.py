import unittest
from payos.type import ItemData, PaymentData, CreatePaymentResult

class TestItemData(unittest.TestCase):
    def test_valid_item_data(self):
        """Test creating a valid ItemData object"""
        item = ItemData(name="Test Item", quantity=1, price=1000)
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.price, 1000)

    def test_invalid_item_data_types(self):
        """Test ItemData with invalid data types"""
        with self.assertRaises(ValueError):
            ItemData(name=123, quantity=1, price=1000)  # invalid name type
        with self.assertRaises(ValueError):
            ItemData(name="Test", quantity="1", price=1000)  # invalid quantity type
        with self.assertRaises(ValueError):
            ItemData(name="Test", quantity=1, price="1000")  # invalid price type

    def test_item_data_to_json(self):
        """Test ItemData to_json method"""
        item = ItemData(name="Test Item", quantity=1, price=1000)
        json_data = item.to_json()
        self.assertEqual(json_data, {
            "name": "Test Item",
            "quantity": 1,
            "price": 1000
        })

class TestPaymentData(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            "orderCode": 12345,
            "amount": 1000000,
            "description": "Test payment",
            "cancelUrl": "https://example.com/cancel",
            "returnUrl": "https://example.com/return"
        }

    def test_valid_payment_data(self):
        """Test creating a valid PaymentData object"""
        payment = PaymentData(**self.valid_data)
        self.assertEqual(payment.orderCode, self.valid_data["orderCode"])
        self.assertEqual(payment.amount, self.valid_data["amount"])
        self.assertEqual(payment.description, self.valid_data["description"])

    def test_payment_data_with_items(self):
        """Test PaymentData with items"""
        items = [
            ItemData(name="Item 1", quantity=1, price=500000),
            ItemData(name="Item 2", quantity=1, price=500000)
        ]
        data = self.valid_data.copy()
        data["items"] = items
        payment = PaymentData(**data)
        self.assertEqual(len(payment.items), 2)
        self.assertEqual(payment.items[0].name, "Item 1")

    def test_invalid_payment_data(self):
        """Test PaymentData with invalid data"""
        invalid_data = self.valid_data.copy()
        invalid_data["orderCode"] = "12345"  # should be int
        with self.assertRaises(ValueError):
            PaymentData(**invalid_data)

    def test_payment_data_to_json(self):
        """Test PaymentData to_json method"""
        payment = PaymentData(**self.valid_data)
        json_data = payment.to_json()
        self.assertEqual(json_data["orderCode"], self.valid_data["orderCode"])
        self.assertEqual(json_data["amount"], self.valid_data["amount"])
        self.assertIsNone(json_data["items"])

class TestCreatePaymentResult(unittest.TestCase):
    def test_create_payment_result(self):
        """Test creating a CreatePaymentResult object"""
        data = {
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
        }
        result = CreatePaymentResult(**data)
        self.assertEqual(result.bin, data["bin"])
        self.assertEqual(result.accountNumber, data["accountNumber"])
        self.assertEqual(result.amount, data["amount"])
        self.assertIsNone(result.expiredAt)

if __name__ == "__main__":
    unittest.main()
