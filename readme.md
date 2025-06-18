# PayOS Python SDK

Một thư viện Python bất đồng bộ (asynchronous) để tương tác với API cổng thanh toán PayOS. Thư viện này giúp bạn dễ dàng tích hợp các dịch vụ thanh toán của PayOS vào ứng dụng Python của mình.

## Mục lục

* [Tính năng](#tính-năng)
* [Cấu trúc dự án](#cấu-trúc-dự-án)
* [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
* [Cài đặt](#cài-đặt)

    * [Cài đặt từ PyPI (khuyên dùng)](#cài-đặt-từ-pypi-khuyên-dùng)
    * [Cài đặt từ mã nguồn](#cài-đặt-từ-mã-nguồn)
* [Cách sử dụng](#cách-sử-dụng)

    * [Khởi tạo SDK](#khởi-tạo-sdk)
    * [Tạo liên kết thanh toán](#tạo-liên-kết-thanh-toán)
    * [Lấy thông tin liên kết thanh toán](#lấy-thông-tin-liên-kết-thanh-toán)
    * [Huỷ liên kết thanh toán](#huỷ-liên-kết-thanh-toán)
    * [Xác nhận URL webhook](#xác-nhận-url-webhook)
    * [Xác minh dữ liệu webhook](#xác-minh-dữ-liệu-webhook)
* [Cấu trúc dữ liệu](#cấu-trúc-dữ-liệu)
* [Xử lý lỗi](#xử-lý-lỗi)
* [Đóng góp](#đóng-góp)
* [Giấy phép](#giấy-phép)

## Tính năng

* Tạo liên kết thanh toán cho đơn hàng.
* Truy xuất thông tin chi tiết về liên kết thanh toán.
* Huỷ bỏ liên kết thanh toán.
* Xác nhận URL webhook với PayOS.
* Xác minh an toàn dữ liệu webhook nhờ vào cơ chế checksum.
* Hỗ trợ hoàn toàn bất đồng bộ (`async`) với `aiohttp` giúp hiệu năng cao.
* Hỗ trợ `type hinting` giúp dễ lập trình và kiểm tra lỗi.
* Cơ chế xử lý lỗi riêng biệt cho các lỗi đặc thù từ API PayOS.

## Cấu trúc dự án

```
root_project/
├── payos/
│   ├── __init__.py           # Biến 'payos' thành package và export các lớp chính
│   ├── constants.py          # Các hằng số API, thông báo lỗi, URL gốc
│   ├── custom_error.py       # Định nghĩa exception PayOSError
│   ├── index.py              # Lớp chính PayOS chứa logic gọi API
│   ├── type.py               # Định nghĩa các kiểu dữ liệu cho request/response
│   └── utils.py              # Các hàm tiện ích (ví dụ tạo chữ ký)
├── tests/
│   ├── __init__.py
│   ├── requirements-test.txt # Dependencies dùng cho test
│   ├── test_payos.py         # Unit test cho lớp PayOS
│   └── test_types.py         # Unit test cho các kiểu dữ liệu
├── pyproject.toml            # Thông tin build và cấu hình project
└── readme.md                 # File này
```

## Yêu cầu hệ thống

* Python 3.7 trở lên (do sử dụng `async/await` và type hinting).
* Thư viện `aiohttp` để gửi request bất đồng bộ.
* Tài khoản merchant tại PayOS với:

    * `Client ID`
    * `API Key`
    * `Checksum Key`

## Cài đặt

### Cài đặt từ PyPI (khuyên dùng)

```bash
pip install payos-async
```

### Cài đặt từ mã nguồn
Nếu bạn muốn chỉnh sửa mã nguồn hoặc đóng góp, có thể cài đặt từ repo:

> [!IMPORTANT]
> Bạn cần cài đặt Python 3.7 trở lên.

Clone mã nguồn về máy:
```bash
git clone https://github.com/ShindouAris/PayOS-Async-SDK.git
cd PayOS-Async-SDK
```
Tiến hành build và cài đặt:
```bash
  pip install build
  python -m build
  pip install dist/payos_async_sdk-0.1.0-py3-none-any.whl
```
## Cách sử dụng

Mọi hàm gọi API đều là **bất đồng bộ**, bạn cần dùng `await`.

### Khởi tạo SDK

```python
from payos import PayOS, PaymentData, ItemData
payos_client = PayOS(
    client_id="YOUR_CLIENT_ID",
    api_key="YOUR_API_KEY",
    checksum_key="YOUR_CHECKSUM_KEY"
)
```

### Tạo liên kết thanh toán

```python
payment_data = PaymentData(
    orderCode=123456,
    amount=1000000,
    description="Thanh toán đơn hàng #123456",
    cancelUrl="https://domain.com/cancel",
    returnUrl="https://domain.com/success",
    items=[
        ItemData(name="Áo thun", quantity=1, price=500000),
        ItemData(name="Quần jean", quantity=1, price=500000)
    ]
)
result = await payos_client.createPaymentLink(payment_data)
print(result.checkoutUrl)
```

### Lấy thông tin thanh toán

```python
info = await payos_client.getPaymentLinkInformation(order_id=123456)
print(info.status, info.amountPaid)
```

### Huỷ thanh toán

```python
await payos_client.cancelPaymentLink(order_id=123456, cancellationReason="Khách yêu cầu huỷ")
```

### Xác nhận URL webhook

```python
webhook_data = {
  # Data nhận được từ payOS khi bạn thiết đặt một webhook
}
await payos_client.confirmWebhook(webhook_data)
```

### Xác minh dữ liệu webhook

```python
verified = payos_client.verifyPaymentWebhookData(webhook_body_dict) 
# webhook_body_dict nhận được khi thiết đặt webhook trong kênh thanh toán
print(verified.orderCode, verified.amount)
```

## Cấu trúc dữ liệu

Tham khảo file `payos/type.py`, gồm:

* `ItemData`: Sản phẩm trong đơn hàng
* `PaymentData`: Dữ liệu tạo đơn
* `CreatePaymentResult`: Kết quả từ `createPaymentLink`
* `Transaction`: Giao dịch liên quan
* `PaymentLinkInformation`: Thông tin liên kết
* `WebhookData`: Dữ liệu webhook đã xác minh

## Xử lý lỗi

* Nếu nhập sai dữ liệu đầu vào → raise `TypeError`, `ValueError`
* Nếu API trả về lỗi → raise `PayOSError`

    * Có `.code` và `.message`
* Nếu chữ ký không khớp → raise `Exception`

Ví dụ:

```python
try:
    await payos_client.createPaymentLink(payment_data)
except PayOSError as e:
    print(f"Lỗi PayOS: {e.code} - {e}")
except Exception as e:
    print(f"Lỗi khác: {e}")
```

## Đóng góp

Rất hoan nghênh đóng góp!

1. Fork repo
2. Tạo branch mới
3. Gửi pull request rõ ràng

## Giấy phép
Mã nguồn được phát hành theo giấy phép **MIT**.