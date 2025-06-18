from payos.constants import ERROR_MESSAGE, ERROR_CODE, PAYOS_BASE_URL
from payos.utils import createSignatureFromObj, createSignatureOfPaymentRequest
from payos.custom_error import PayOSError
from payos.type import (
    PaymentData,
    CreatePaymentResult,
    Transaction,
    PaymentLinkInformation,
    WebhookData,
)
from typing import Union, Optional
from aiohttp import ClientSession

class PayOS:
    def __init__(
        self, client_id: str, api_key: str, checksum_key: str, partner_code: str = None
    ) -> None:
        # Kiểm tra kiểu dữ liệu của client_id
        if not isinstance(client_id, str):
            raise TypeError("client_id phải là một chuỗi.")

        # Kiểm tra kiểu dữ liệu của api_key
        if not isinstance(api_key, str):
            raise TypeError("api_key phải là một chuỗi.")

        # Kiểm tra kiểu dữ liệu của checksum_key
        if not isinstance(checksum_key, str):
            raise TypeError("checksum_key phải là một chuỗi.")

        self.__client_id = client_id
        self.__api_key = api_key
        self.__checksum_key = checksum_key
        self.__partner_code = partner_code

    async def createPaymentLink(self, paymentData: PaymentData) -> Optional[CreatePaymentResult]:
        if not isinstance(paymentData, PaymentData):
            raise ValueError(
                f"{ERROR_MESSAGE['INVALID_PARAMETER']} - paymentData phải là một đối tượng của lớp PaymentData."
            )

        url = f"{PAYOS_BASE_URL}/v2/payment-requests"
        paymentData.signature = createSignatureOfPaymentRequest(
            paymentData, self.__checksum_key
        )
        headers = {
            "Content-Type": "application/json",  # Loại nội dung của body
            "x-client-id": self.__client_id,
            "x-api-key": self.__api_key,
        }
        if self.__partner_code is not None:
            headers["x-partner-code"] = self.__partner_code

        async with ClientSession() as session:
            paymentLinkRes = await session.post(url, json=paymentData.to_json(), headers=headers)
            if paymentLinkRes.ok:
                paymentLinkRes = await paymentLinkRes.json()
                if paymentLinkRes["code"] == "00":
                    paymentLinkResSignature = createSignatureFromObj(
                        paymentLinkRes["data"], self.__checksum_key
                    )
                    if paymentLinkResSignature != paymentLinkRes["signature"]:
                        raise Exception(ERROR_MESSAGE["DATA_NOT_INTEGRITY"])
                    if paymentLinkRes["data"] is not None:
                        return CreatePaymentResult(**paymentLinkRes["data"])
                    raise PayOSError(
                        code=paymentLinkRes["code"], message=paymentLinkRes["desc"]
                    )
                else:
                    raise PayOSError(
                        code=paymentLinkRes["code"], message=paymentLinkRes["desc"]
                    )
        raise PayOSError(
            ERROR_CODE["INTERNAL_SERVER_ERROR"], ERROR_MESSAGE["INTERNAL_SERVER_ERROR"]
        )

    async def getPaymentLinkInformation(self, orderId: Union[str, int]) -> Optional[PaymentLinkInformation]:
        if type(orderId) not in [str, int]:
            raise ValueError(ERROR_MESSAGE["INVALID_PARAMETER"])
        url = f"{PAYOS_BASE_URL}/v2/payment-requests/{orderId}"
        headers = {
            "Content-Type": "application/json",  # Loại nội dung của body
            "x-client-id": self.__client_id,
            "x-api-key": self.__api_key,
        }
        async with ClientSession() as session:
            paymentLinkInfoRes = await session.get(url, headers=headers)
            if paymentLinkInfoRes.ok:
                paymentLinkInfoRes = await paymentLinkInfoRes.json()
                if paymentLinkInfoRes["code"] == "00":
                    paymentLinkInfoResSignature = createSignatureFromObj(
                        paymentLinkInfoRes["data"], self.__checksum_key
                    )
                    if paymentLinkInfoResSignature != paymentLinkInfoRes["signature"]:
                        raise Exception(ERROR_MESSAGE["DATA_NOT_INTEGRITY"])
                    if paymentLinkInfoRes["data"] is not None:
                        paymentLinkInfoRes["data"]["transactions"] = [
                            Transaction(**x)
                            for x in paymentLinkInfoRes["data"]["transactions"]
                        ]
                        return PaymentLinkInformation(**paymentLinkInfoRes["data"])
                    raise PayOSError(
                        code=paymentLinkInfoRes["code"], message=paymentLinkInfoRes["desc"]
                    )
                else:
                    raise PayOSError(
                        code=paymentLinkInfoRes["code"], message=paymentLinkInfoRes["desc"]
                    )
        raise PayOSError(
            ERROR_CODE["INTERNAL_SERVER_ERROR"], ERROR_MESSAGE["INTERNAL_SERVER_ERROR"]
        )

    async def confirmWebhook(self, webhookUrl: str) -> Optional[str]:
        if webhookUrl is None or len(webhookUrl) == 0:
            raise ValueError(ERROR_MESSAGE["INVALID_PARAMETER"])

        url = f"{PAYOS_BASE_URL}/confirm-webhook"
        data = {"webhookUrl": webhookUrl}
        headers = {
            "Content-Type": "application/json",  # Loại nội dung của body
            "x-client-id": self.__client_id,
            "x-api-key": self.__api_key,
        }
        async with ClientSession() as session:
            responseConfirm = await session.post(url=url, json=data, headers=headers)
            if responseConfirm.status == 200:
                return webhookUrl
            elif responseConfirm.status == 404:
                raise PayOSError(
                    ERROR_CODE["INTERNAL_SERVER_ERROR"],
                    ERROR_MESSAGE["WEBHOOK_URL_INVALID"],
                )
            elif responseConfirm.status == 401:
                raise PayOSError(ERROR_CODE["UNAUTHORIZED"], ERROR_MESSAGE["UNAUTHORIZED"])
            raise PayOSError(
                ERROR_CODE["INTERNAL_SERVER_ERROR"], ERROR_MESSAGE["INTERNAL_SERVER_ERROR"]
            )

    async def cancelPaymentLink(
        self, orderId: Union[str, int], cancellationReason: str = None
    ) -> Optional[PaymentLinkInformation]:
        if type(orderId) not in [str, int]:
            raise ValueError(ERROR_MESSAGE["INVALID_PARAMETER"])
        url = f"{PAYOS_BASE_URL}/v2/payment-requests/{orderId}/cancel"
        cancellationReason = (
            {"cancellationReason": cancellationReason}
            if cancellationReason is not None
            else None
        )
        headers = {
            "Content-Type": "application/json",  # Loại nội dung của body
            "x-client-id": self.__client_id,
            "x-api-key": self.__api_key,
        }
        async with ClientSession() as session:
            cancelPaymentLinkResponse = await session.post(
                url, headers=headers, json=cancellationReason
            )
            if cancelPaymentLinkResponse.ok:
                cancelPaymentLinkResponse = await cancelPaymentLinkResponse.json()
                if cancelPaymentLinkResponse["code"] == "00":
                    paymentLinkInfoResSignature = createSignatureFromObj(
                        cancelPaymentLinkResponse["data"], self.__checksum_key
                    )
                    if (
                        paymentLinkInfoResSignature
                        != cancelPaymentLinkResponse["signature"]
                    ):
                        raise Exception(ERROR_MESSAGE["DATA_NOT_INTEGRITY"])
                    if cancelPaymentLinkResponse["data"] is not None:
                        cancelPaymentLinkResponse["data"]["transactions"] = [
                            Transaction(**x)
                            for x in cancelPaymentLinkResponse["data"]["transactions"]
                        ]
                        return PaymentLinkInformation(**cancelPaymentLinkResponse["data"])
                    raise PayOSError(
                        code=cancelPaymentLinkResponse["code"],
                        message=cancelPaymentLinkResponse["desc"],
                    )
                else:
                    raise PayOSError(
                        code=cancelPaymentLinkResponse["code"],
                        message=cancelPaymentLinkResponse["desc"],
                    )
        raise PayOSError(
            ERROR_CODE["INTERNAL_SERVER_ERROR"], ERROR_MESSAGE["INTERNAL_SERVER_ERROR"]
        )

    def verifyPaymentWebhookData(self, webhookBody) -> Optional[WebhookData]:
        data = webhookBody["data"]
        signature = webhookBody["signature"]
        if data is None:
            raise ValueError(ERROR_MESSAGE["NO_DATA"])
        if signature is None:
            raise ValueError(ERROR_MESSAGE["NO_SIGNATURE"])
        signData = createSignatureFromObj(data=data, key=self.__checksum_key)

        if signData != signature:
            raise Exception(ERROR_MESSAGE["DATA_NOT_INTEGRITY"])
        return WebhookData(**data)