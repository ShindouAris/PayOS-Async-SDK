# PayOS Python SDK

An asynchronous Python SDK for interacting with the PayOS payment gateway API. This library helps you easily integrate PayOS payment services into your Python applications.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Install via PyPI (Recommended)](#install-via-pypi-recommended)
  - [Install from Source](#install-from-source)
- [Usage](#usage)
  - [Initialization](#initialization)
  - [Creating a Payment Link](#creating-a-payment-link)
  - [Getting Payment Link Information](#getting-payment-link-information)
  - [Canceling a Payment Link](#canceling-a-payment-link)
  - [Confirming a Webhook URL](#confirming-a-webhook-url)
  - [Verifying Webhook Data](#verifying-webhook-data)
- [Data Structures](#data-structures)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Features

-   Create payment links for orders.
-   Retrieve detailed information about a payment link.
-   Cancel existing payment links.
-   Confirm your webhook URL with PayOS.
-   Securely verify incoming webhook data using checksums.
-   Asynchronous operations using `aiohttp` for non-blocking I/O.
-   Type-hinted for better development experience and code quality.
-   Custom error handling for API-specific issues.

## Project Structure

```
root_project/
├── payos/
│   ├── __init__.py         # Makes 'payos' a package and exports main classes
│   ├── constants.py        # API constants, error messages, base URL
│   ├── custom_error.py     # Custom PayOSError exception
│   ├── index.py            # Core PayOS class with API interaction logic
│   ├── type.py             # Data Pydantic models for request/response structures
│   └── utils.py            # Utility functions (e.g., signature generation)
├── tests/
│   ├── __init__.py
│   ├── requirements-test.txt # Test-specific dependencies (for development)
│   ├── test_payos.py       # Unit tests for PayOS class methods (for development)
│   └── test_types.py       # Unit tests for data types (for development)
├── pyproject.toml          # Project metadata and build configuration
└── readme.md               # This file
```

## Prerequisites

-   Python 3.7+ (due to `async/await` and type hinting)
-   `aiohttp` library for asynchronous HTTP requests.
-   A PayOS merchant account with:
    -   `Client ID`
    -   `API Key`
    -   `Checksum Key`

## Installation

### Install via PyPI (Recommended)

If the package is published on the Python Package Index (PyPI), you can install it using pip:

```bash
pip install payos-async-sdk
```
This will also install `aiohttp` as a dependency if it's correctly specified in the package's `pyproject.toml` or `setup.py`.

### Install from Source


## Usage

All API interaction methods are asynchronous and need to be `await`ed.

### Initialization

First, import the `PayOS` class and initialize it with your credentials.

```python
import asyncio
from payos import PayOS, PaymentData, ItemData # Import necessary classes
from datetime import datetime, timedelta # timedelta for expiredAt example

CLIENT_ID = "your-client-id"
API_KEY = "your-api-key"
CHECKSUM_KEY = "your-checksum-key"
# Optional: PARTNER_CODE = "your-partner-code"

payos_client = PayOS(
    client_id=CLIENT_ID,
    api_key=API_KEY,
    checksum_key=CHECKSUM_KEY
    # partner_code=PARTNER_CODE # if you have one
)
```

### Creating a Payment Link

To create a payment link, you need to provide `PaymentData`.

```python
async def create_payment():
    order_code = int(datetime.now().timestamp()) # Example: unique order code

    payment_items = [
        ItemData(name="Laptop Pro", quantity=1, price=20000000),
        ItemData(name="Mouse Wireless", quantity=1, price=500000)
    ]

    payment_data = PaymentData(
        orderCode=order_code,
        amount=20500000,
        description="Thanh toan don hang #{}".format(order_code),
        items=payment_items,
        cancelUrl="https://your-domain.com/cancel-order",
        returnUrl="https://your-domain.com/payment-success",
        # Optional fields:
        # buyerName="Nguyen Van A",
        # buyerEmail="nguyenvana@example.com",
        # buyerPhone="0987654321",
        # buyerAddress="123 Duong ABC, Quan 1, TP XYZ",
        # expiredAt=int((datetime.now() + timedelta(days=1)).timestamp()) # e.g., expires in 1 day
    )

    try:
        payment_link_info = await payos_client.createPaymentLink(payment_data)
        print(f"Payment Link ID: {payment_link_info.paymentLinkId}")
        print(f"Checkout URL: {payment_link_info.checkoutUrl}")
        print(f"QR Code Data: {payment_link_info.qrCode}")
        return payment_link_info
    except Exception as e:
        print(f"Error creating payment link: {e}")
        # Handle specific PayOSError if needed
        # from payos.custom_error import PayOSError
        # if isinstance(e, PayOSError):
        #     print(f"PayOS Error Code: {e.code}, Message: {str(e)}")

# Example of running an async function:
# if __name__ == "__main__":
#     asyncio.run(create_payment())
```

### Getting Payment Link Information

Retrieve details of an existing payment link using its `orderId`.

```python
async def get_payment_info(order_id: int): # or str
    try:
        payment_info = await payos_client.getPaymentLinkInformation(order_id)
        print(f"Order ID: {payment_info.orderCode}")
        print(f"Status: {payment_info.status}")
        print(f"Amount: {payment_info.amount}")
        print(f"Amount Paid: {payment_info.amountPaid}")
        if payment_info.transactions:
            print("Transactions:")
            for tx in payment_info.transactions:
                print(f"  - Ref: {tx.reference}, Amount: {tx.amount}, Time: {tx.transactionDateTime}")
        return payment_info
    except Exception as e:
        print(f"Error getting payment link information: {e}")

# Example:
# if __name__ == "__main__":
#     # Assuming you have an order_id from a created payment or other source
#     asyncio.run(get_payment_info(123456789))
```

### Canceling a Payment Link

Cancel a payment link if it's no longer needed.

```python
async def cancel_payment_link(order_id: int, reason: str = None): # order_id can also be str
    try:
        canceled_info = await payos_client.cancelPaymentLink(order_id, cancellationReason=reason)
        print(f"Order ID: {canceled_info.orderCode}")
        print(f"Status: {canceled_info.status}")
        if canceled_info.cancellationReason:
            print(f"Cancellation Reason: {canceled_info.cancellationReason}")
        return canceled_info
    except Exception as e:
        print(f"Error canceling payment link: {e}")

# Example:
# if __name__ == "__main__":
#     asyncio.run(cancel_payment_link(123456789, "Customer request"))
```

### Confirming a Webhook URL

This is typically a one-time setup step to register your webhook endpoint with PayOS.

```python
async def confirm_my_webhook():
    webhook_url = "https://your-domain.com/payos-webhook-handler"
    try:
        confirmed_url = await payos_client.confirmWebhook(webhook_url)
        print(f"Webhook URL successfully confirmed: {confirmed_url}")
        return confirmed_url
    except Exception as e:
        print(f"Error confirming webhook URL: {e}")

# Example:
# if __name__ == "__main__":
#     asyncio.run(confirm_my_webhook())
```

### Verifying Webhook Data

When PayOS sends a notification to your webhook endpoint, you must verify its authenticity.

```python
# This function would be part of your webhook handler (e.g., in a Flask/FastAPI app)
# webhook_body is the raw JSON payload received from PayOS.
def handle_webhook(webhook_body: dict):
    try:
        # The webhook_body should be a dictionary parsed from the JSON request body
        # It typically has 'data', 'signature', 'code', 'desc' keys.
        verified_data = payos_client.verifyPaymentWebhookData(webhook_body)

        print(f"Webhook data verified successfully!")
        print(f"Order Code: {verified_data.orderCode}")
        print(f"Amount: {verified_data.amount}")
        print(f"Description: {verified_data.description}")
        print(f"Status Code: {verified_data.code}") # e.g., "00" for success
        print(f"Status Desc: {verified_data.desc}")

        # Process the payment status update based on verified_data
        # For example, update your database, notify the user, etc.
        if verified_data.code == "00":
            print("Payment was successful.")
            # Your logic for successful payment
        else:
            print(f"Payment update with status: {verified_data.desc}")
            # Your logic for other statuses

        return verified_data
    except ValueError as ve: # For NO_DATA, NO_SIGNATURE errors
        print(f"Webhook data validation error: {ve}")
        # Respond with HTTP 400 Bad Request
    except Exception as e: # For DATA_NOT_INTEGRITY or other errors
        print(f"Webhook verification failed: {e}")
        # Respond with HTTP 400 Bad Request or log an internal server error

# Example (conceptual, how you'd get webhook_body depends on your web framework):
# received_payload = {
#     "code": "00",
#     "desc": "Thành công",
#     "data": {
#         "orderCode": 1698855400,
#         "amount": 20500000,
#         "description": "Thanh toan don hang #1698855400",
#         "accountNumber": "PAYOS_ACC_NUMBER",
#         "reference": "PAYMENT_REF_123",
#         "transactionDateTime": "2023-11-01T17:00:00Z",
#         "paymentLinkId": "link_id_abcxyz",
#         "code": "00", # status code within data
#         "desc": "Thành công", # status desc within data
#         "currency": "VND"
#         # ... other fields as per WebhookData type ...
#     },
#     "signature": "generated_signature_from_payos"
# }
# handle_webhook(received_payload)
```
**Note:** The `verifyPaymentWebhookData` method is synchronous as it only performs cryptographic checks on the provided data.

## Data Structures

The SDK uses specific data classes (mostly dataclasses or custom classes with `to_json` methods) for requests and responses, found in `payos/type.py`:

-   `ItemData`: Represents an item in an order.
    -   `name: str`
    -   `quantity: int`
    -   `price: int`
-   `PaymentData`: Used for creating a payment link.
    -   `orderCode: int` (required)
    -   `amount: int` (required)
    -   `description: str` (required)
    -   `cancelUrl: str` (required)
    -   `returnUrl: str` (required)
    -   `items: List[ItemData]` (optional)
    -   `buyerName: str` (optional)
    -   `buyerEmail: str` (optional)
    -   `buyerPhone: str` (optional)
    -   `buyerAddress: str` (optional)
    -   `expiredAt: int` (optional, Unix timestamp)
    -   `signature: str` (auto-generated by the SDK)
-   `CreatePaymentResult`: Response from creating a payment link.
    -   Includes `bin`, `accountNumber`, `checkoutUrl`, `qrCode`, `paymentLinkId`, etc.
-   `Transaction`: Represents a single transaction associated with a payment link.
-   `PaymentLinkInformation`: Detailed information about a payment link.
    -   Includes `id`, `orderCode`, `status`, `amountPaid`, `transactions: List[Transaction]`, etc.
-   `WebhookData`: Parsed and verified data from an incoming webhook.
    -   Includes `orderCode`, `amount`, `reference`, `transactionDateTime`, `code` (status), `desc` (status description), etc.

Refer to `payos/type.py` for the full structure of these classes.

## Error Handling

-   The SDK raises standard Python exceptions like `TypeError` or `ValueError` for invalid input parameters (e.g., wrong data type, missing required fields).
-   For API-related errors (e.g., authentication failure, invalid request to PayOS server), a custom `PayOSError` (from `payos.custom_error`) is raised.
    -   `PayOSError` has two main attributes:
        -   `code: str`: The error code from PayOS (e.g., "20", "401").
        -   `message: str`: A descriptive error message.
-   Signature verification failures in responses or webhooks will raise a generic `Exception` with a message like `ERROR_MESSAGE['DATA_NOT_INTEGRITY']`.

Always wrap API calls in `try...except` blocks to handle potential errors gracefully.

```python
from payos.custom_error import PayOSError

try:
    # ... some PayOS API call ...
    pass
except PayOSError as pe:
    print(f"PayOS API Error - Code: {pe.code}, Message: {str(pe)}")
except ValueError as ve:
    print(f"Input validation error: {ve}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## Contributing

Contributions are welcome! If you'd like to contribute, please:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Add or update tests for your changes (tests are in the `tests/` directory and are valuable for development and CI, even if not run by end-users).
4.  Ensure all tests pass.
5.  Submit a pull request with a clear description of your changes.

## License
