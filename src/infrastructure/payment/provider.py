"""Payment integration for Payme and Click — haqiqiy API integratsiyasi."""

import hashlib
import hmac
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum

import httpx

from src.config.logging import get_logger
from src.infrastructure.db.models.subscription import SubscriptionModel

logger = get_logger(__name__)


class PaymentStatus(Enum):
    """To'lov holati."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class SubscriptionTier(Enum):
    """Obuna darajasi."""

    FREE = "free"
    PRO = "pro"


@dataclass
class PaymentResult:
    """To'lov natijasi."""

    success: bool
    transaction_id: str | None = None
    status: PaymentStatus = PaymentStatus.PENDING
    message: str = ""
    payment_url: str | None = None


@dataclass
class Subscription:
    """Obuna ma'lumotlari."""

    user_id: int
    tier: SubscriptionTier
    started_at: datetime
    expires_at: datetime | None = None
    payment_method: str | None = None


class PaymentProvider(ABC):
    """To'lov provideri abstraktsiyasi."""

    @abstractmethod
    async def create_payment(
        self, amount: float, user_id: int, description: str
    ) -> PaymentResult:
        """To'lov yaratish."""
        ...

    @abstractmethod
    async def check_payment(self, transaction_id: str) -> PaymentResult:
        """To'lov holatini tekshirish."""
        ...

    @abstractmethod
    async def refund(self, transaction_id: str) -> PaymentResult:
        """To'lovni qaytarish."""
        ...


class PaymeProvider(PaymentProvider):
    """Payme to'lov provideri — haqiqiy API integratsiyasi.

    API Docs: https://payme.uz/merchant
    """

    BASE_URL = "https://payme.uz/api"

    def __init__(self, merchant_id: str, secret_key: str):
        self.merchant_id = merchant_id
        self.secret_key = secret_key

    def _generate_auth_header(self, method: str) -> str:
        """Payme uchun auth header generatsiya qilish."""
        timestamp = str(int(datetime.now().timestamp()))
        data = f"{self.merchant_id}:{self.secret_key}:{timestamp}"
        auth_token = hashlib.sha256(data.encode()).hexdigest()
        return f"{self.merchant_id}:{auth_token}:{timestamp}"

    async def _make_request(self, method: str, params: dict) -> dict:
        """Payme API ga so'rov yuborish."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self._generate_auth_header(method)}",
        }

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}",
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

    async def create_payment(
        self, amount: float, user_id: int, description: str
    ) -> PaymentResult:
        """Payme orqali to'lov yaratish.

        Amount tiyinda (UZS) — masalan 99900 = $9.99
        """
        amount_tiyin = int(amount * 100)

        try:
            params = {
                "merchant_id": self.merchant_id,
                "amount": amount_tiyin,
                "currency": 860,  # UZS
                "account": {"user_id": str(user_id)},
                "description": description,
                "return_url": "https://disipl.uz/payment/success",
                "cancel_url": "https://disipl.uz/payment/cancel",
            }

            data = await self._make_request("CreateTransaction", params)

            if data.get("result"):
                transaction_id = str(data["result"]["transaction"])
                payment_url = f"https://payme.uz/pay/{transaction_id}"

                logger.info(
                    f"Payme payment created: user={user_id}, "
                    f"tx={transaction_id}, amount={amount_tiyin} tiyin"
                )

                return PaymentResult(
                    success=True,
                    transaction_id=transaction_id,
                    status=PaymentStatus.PENDING,
                    message="To'lov yaratildi",
                    payment_url=payment_url,
                )
            else:
                error = data.get("error", {})
                error_code = error.get("code", "unknown")
                error_message = error.get("message", "Noma'lum xato")

                logger.error(
                    f"Payme create payment error: code={error_code}, "
                    f"msg={error_message}, user={user_id}"
                )

                return PaymentResult(
                    success=False,
                    status=PaymentStatus.FAILED,
                    message=f"Xato: {error_message} (kod: {error_code})",
                )

        except httpx.TimeoutException:
            logger.error(f"Payme API timeout: user={user_id}")
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="Payme API vaqt tugadi, qayta urinib ko'ring",
            )
        except Exception as e:
            logger.error(f"Payme payment error: {e}, user={user_id}")
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message=f"To'lov yaratishda xato: {e!s}",
            )

    async def check_payment(self, transaction_id: str) -> PaymentResult:
        """To'lov holatini tekshirish."""
        try:
            params = {"id": int(transaction_id)}
            data = await self._make_request("GetTransaction", params)

            if data.get("result"):
                state = data["result"].get("state", 0)
                # State: 0 = yangi, 1 = tasdiqlangan, 2 = bekor qilingan
                if state == 1:
                    logger.info(f"Payme payment completed: tx={transaction_id}")
                    return PaymentResult(
                        success=True,
                        transaction_id=transaction_id,
                        status=PaymentStatus.COMPLETED,
                        message="To'lov muvaffaqiyatli amalga oshirildi",
                    )
                elif state == 2:
                    return PaymentResult(
                        success=True,
                        transaction_id=transaction_id,
                        status=PaymentStatus.REFUNDED,
                        message="To'lov bekor qilindi",
                    )
                else:
                    return PaymentResult(
                        success=True,
                        transaction_id=transaction_id,
                        status=PaymentStatus.PENDING,
                        message="To'lov hali to'liq emas",
                    )

            return PaymentResult(
                success=False,
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                message="Tranzaksiya topilmadi",
            )

        except Exception as e:
            logger.error(f"Payme check payment error: {e}, tx={transaction_id}")
            return PaymentResult(
                success=False,
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                message=f"To'lovni tekshirishda xato: {e!s}",
            )

    async def refund(self, transaction_id: str) -> PaymentResult:
        """To'lovni qaytarish."""
        try:
            params = {"id": int(transaction_id)}
            data = await self._make_request("CancelTransaction", params)

            if data.get("result"):
                logger.info(f"Payme refund successful: tx={transaction_id}")
                return PaymentResult(
                    success=True,
                    transaction_id=transaction_id,
                    status=PaymentStatus.REFUNDED,
                    message="To'lov qaytarildi",
                )
            else:
                error = data.get("error", {})
                return PaymentResult(
                    success=False,
                    transaction_id=transaction_id,
                    status=PaymentStatus.FAILED,
                    message=f"Qaytarishda xato: {error.get('message', 'Noma\'lum')}",
                )

        except Exception as e:
            logger.error(f"Payme refund error: {e}, tx={transaction_id}")
            return PaymentResult(
                success=False,
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                message=f"To'lovni qaytarishda xato: {e!s}",
            )


class ClickProvider(PaymentProvider):
    """Click to'lov provideri — haqiqiy API integratsiyasi.

    API Docs: https://docs.click.uz
    """

    BASE_URL = "https://api.click.uz/v1/merchant"

    def __init__(self, merchant_id: str, secret_key: str):
        self.merchant_id = merchant_id
        self.secret_key = secret_key

    def _generate_signature(self, data: str) -> str:
        """Click uchun imzo generatsiya qilish."""
        return hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()

    async def _make_request(self, method: str, endpoint: str, params: dict) -> dict:
        """Click API ga so'rov yuborish."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sign_data = f"{self.merchant_id}{timestamp}"
        signature = self._generate_signature(sign_data)

        headers = {
            "Content-Type": "application/json",
            "X-Auth": f"{self.merchant_id}:{signature}",
            "X-Signature": signature,
            "X-Timestamp": timestamp,
        }

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.BASE_URL}/{endpoint}",
                json=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

    async def create_payment(
        self, amount: float, user_id: int, description: str
    ) -> PaymentResult:
        """Click orqali to'lov yaratish.

        Amount so'mda — masalan 99900 = 99,900 so'm
        """
        amount_som = int(amount * 100)

        try:
            params = {
                "amount": amount_som,
                "currency": 860,  # UZS
                "account": {"user_id": str(user_id)},
                "description": description,
            }

            data = await self._make_request("POST", "payments/create", params)

            if "payment_id" in data:
                payment_id = str(data["payment_id"])
                payment_url = data.get("pay_url", f"https://click.uz/pay/{payment_id}")

                logger.info(
                    f"Click payment created: user={user_id}, "
                    f"payment_id={payment_id}, amount={amount_som} so'm"
                )

                return PaymentResult(
                    success=True,
                    transaction_id=payment_id,
                    status=PaymentStatus.PENDING,
                    message="To'lov yaratildi",
                    payment_url=payment_url,
                )
            else:
                error_code = data.get("error_code", "unknown")
                error_note = data.get("error_note", "Noma'lum xato")

                logger.error(
                    f"Click create payment error: code={error_code}, "
                    f"note={error_note}, user={user_id}"
                )

                return PaymentResult(
                    success=False,
                    status=PaymentStatus.FAILED,
                    message=f"Xato: {error_note} (kod: {error_code})",
                )

        except httpx.TimeoutException:
            logger.error(f"Click API timeout: user={user_id}")
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message="Click API vaqt tugadi, qayta urinib ko'ring",
            )
        except Exception as e:
            logger.error(f"Click payment error: {e}, user={user_id}")
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                message=f"To'lov yaratishda xato: {e!s}",
            )

    async def check_payment(self, transaction_id: str) -> PaymentResult:
        """To'lov holatini tekshirish."""
        try:
            data = await self._make_request("GET", f"payments/{transaction_id}", {})

            if "status" in data:
                status_val = data["status"]
                # Status: 0 = yangi, 1 = tasdiqlangan, -1 = bekor qilingan
                if status_val == 1:
                    logger.info(f"Click payment completed: tx={transaction_id}")
                    return PaymentResult(
                        success=True,
                        transaction_id=transaction_id,
                        status=PaymentStatus.COMPLETED,
                        message="To'lov muvaffaqiyatli amalga oshirildi",
                    )
                elif status_val == -1:
                    return PaymentResult(
                        success=True,
                        transaction_id=transaction_id,
                        status=PaymentStatus.REFUNDED,
                        message="To'lov bekor qilindi",
                    )
                else:
                    return PaymentResult(
                        success=True,
                        transaction_id=transaction_id,
                        status=PaymentStatus.PENDING,
                        message="To'lov hali to'liq emas",
                    )

            return PaymentResult(
                success=False,
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                message="Tranzaksiya topilmadi",
            )

        except Exception as e:
            logger.error(f"Click check payment error: {e}, tx={transaction_id}")
            return PaymentResult(
                success=False,
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                message=f"To'lovni tekshirishda xato: {e!s}",
            )

    async def refund(self, transaction_id: str) -> PaymentResult:
        """To'lovni qaytarish."""
        try:
            data = await self._make_request(
                "POST", f"payments/{transaction_id}/cancel", {}
            )

            if data.get("status") == -1:
                logger.info(f"Click refund successful: tx={transaction_id}")
                return PaymentResult(
                    success=True,
                    transaction_id=transaction_id,
                    status=PaymentStatus.REFUNDED,
                    message="To'lov qaytarildi",
                )
            else:
                return PaymentResult(
                    success=False,
                    transaction_id=transaction_id,
                    status=PaymentStatus.FAILED,
                    message="Qaytarishda xato",
                )

        except Exception as e:
            logger.error(f"Click refund error: {e}, tx={transaction_id}")
            return PaymentResult(
                success=False,
                transaction_id=transaction_id,
                status=PaymentStatus.FAILED,
                message=f"To'lovni qaytarishda xato: {e!s}",
            )


class SubscriptionService:
    """Obuna xizmati — DB bilan ishlaydi."""

    PRO_PRICE_USD = 9.99
    PRO_DURATION_DAYS = 30

    def __init__(self, payment_provider: PaymentProvider, session=None):
        self.payment_provider = payment_provider
        self._session = session

    async def subscribe_pro(
        self, user_id: int, payment_method: str = "payme"
    ) -> PaymentResult:
        """Pro obunaga o'tish."""
        result = await self.payment_provider.create_payment(
            amount=self.PRO_PRICE_USD,
            user_id=user_id,
            description="Disipl Pro Subscription (Monthly)",
        )

        if result.success and self._session:
            await self._save_subscription(
                user_id=user_id,
                tier="pro",
                payment_method=payment_method,
                transaction_id=result.transaction_id,
            )

        if result.success:
            logger.info(f"User {user_id} subscribed to Pro via {payment_method}")

        return result

    async def check_subscription(self, user_id: int) -> Subscription:
        """Obuna holatini tekshirish."""
        if self._session:
            return await self._get_active_subscription(user_id)

        return Subscription(
            user_id=user_id,
            tier=SubscriptionTier.FREE,
            started_at=datetime.now(),
        )

    async def _save_subscription(
        self,
        user_id: int,
        tier: str,
        payment_method: str,
        transaction_id: str | None,
    ) -> None:
        """Obunani DB ga saqlash."""
        from sqlalchemy import update

        stmt = (
            update(SubscriptionModel.__table__)
            .where(
                SubscriptionModel.__table__.c.user_id == user_id,
                SubscriptionModel.__table__.c.is_active,
            )
            .values(is_active=False)
        )
        await self._session.execute(stmt)

        subscription = SubscriptionModel(
            user_id=user_id,
            tier=tier,
            started_at=datetime.now(UTC).replace(tzinfo=None),
            expires_at=datetime.now(UTC).replace(tzinfo=None)
            + timedelta(days=self.PRO_DURATION_DAYS),
            payment_method=payment_method,
            transaction_id=transaction_id,
            is_active=True,
        )
        self._session.add(subscription)
        await self._session.flush()

    async def _get_active_subscription(self, user_id: int) -> Subscription:
        """DB dan faol obunani olish."""
        from sqlalchemy import select

        result = await self._session.execute(
            select(SubscriptionModel).where(
                SubscriptionModel.user_id == user_id,
                SubscriptionModel.is_active,
            )
        )
        sub = result.scalar_one_or_none()

        if sub and sub.expires_at and sub.expires_at > datetime.now(UTC):
            return Subscription(
                user_id=user_id,
                tier=SubscriptionTier(sub.tier),
                started_at=sub.started_at,
                expires_at=sub.expires_at,
                payment_method=sub.payment_method,
            )

        return Subscription(
            user_id=user_id,
            tier=SubscriptionTier.FREE,
            started_at=datetime.now(),
        )
