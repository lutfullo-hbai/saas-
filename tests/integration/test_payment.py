"""Payment provider testlari."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.infrastructure.payment.provider import (
    ClickProvider,
    PaymentResult,
    PaymentStatus,
    PaymeProvider,
    SubscriptionService,
    SubscriptionTier,
)


class TestPaymeProvider:
    """Payme provider testlari."""

    def test_create_payment_success(self):
        provider = PaymeProvider(merchant_id="test_merchant", secret_key="test_secret")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"transaction": 12345}
        }
        mock_response.raise_for_status = MagicMock()

        import asyncio
        from unittest.mock import AsyncMock

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=AsyncMock(post=AsyncMock(return_value=mock_response))
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)

            result = asyncio.run(
                provider.create_payment(amount=9.99, user_id=1, description="Test")
            )

        assert result.success is True
        assert result.transaction_id == "12345"
        assert result.status == PaymentStatus.PENDING

    def test_create_payment_api_error(self):
        provider = PaymeProvider(merchant_id="test_merchant", secret_key="test_secret")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "error": {"code": -31001, "message": "Merchant not found"}
        }
        mock_response.raise_for_status = MagicMock()

        import asyncio

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=AsyncMock(post=AsyncMock(return_value=mock_response))
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)

            result = asyncio.run(
                provider.create_payment(amount=9.99, user_id=1, description="Test")
            )

        assert result.success is False
        assert result.status == PaymentStatus.FAILED

    def test_check_payment_completed(self):
        provider = PaymeProvider(merchant_id="test_merchant", secret_key="test_secret")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {"state": 1}
        }
        mock_response.raise_for_status = MagicMock()

        import asyncio

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=AsyncMock(post=AsyncMock(return_value=mock_response))
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)

            result = asyncio.run(provider.check_payment("12345"))

        assert result.success is True
        assert result.status == PaymentStatus.COMPLETED


class TestClickProvider:
    """Click provider testlari."""

    def test_create_payment_success(self):
        provider = ClickProvider(merchant_id="test_merchant", secret_key="test_secret")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "payment_id": 67890,
            "pay_url": "https://click.uz/pay/67890",
        }
        mock_response.raise_for_status = MagicMock()

        import asyncio

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=AsyncMock(request=AsyncMock(return_value=mock_response))
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)

            result = asyncio.run(
                provider.create_payment(amount=99900, user_id=1, description="Test")
            )

        assert result.success is True
        assert result.transaction_id == "67890"

    def test_create_payment_error(self):
        provider = ClickProvider(merchant_id="test_merchant", secret_key="test_secret")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error_code": -1,
            "error_note": "Invalid merchant",
        }
        mock_response.raise_for_status = MagicMock()

        import asyncio

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=AsyncMock(request=AsyncMock(return_value=mock_response))
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)

            result = asyncio.run(
                provider.create_payment(amount=99900, user_id=1, description="Test")
            )

        assert result.success is False
        assert result.status == PaymentStatus.FAILED


class TestSubscriptionService:
    """Subscription service testlari."""

    def test_subscribe_pro_calls_payment(self):
        mock_provider = AsyncMock()
        mock_provider.create_payment.return_value = PaymentResult(
            success=True,
            transaction_id="tx_123",
            status=PaymentStatus.PENDING,
        )

        service = SubscriptionService(payment_provider=mock_provider)

        import asyncio

        result = asyncio.run(service.subscribe_pro(user_id=1))

        assert result.success is True
        mock_provider.create_payment.assert_called_once_with(
            amount=9.99,
            user_id=1,
            description="Disipl Pro Subscription (Monthly)",
        )

    def test_check_subscription_free_by_default(self):
        mock_provider = AsyncMock()
        service = SubscriptionService(payment_provider=mock_provider)

        import asyncio

        sub = asyncio.run(service.check_subscription(user_id=1))

        assert sub.tier == SubscriptionTier.FREE

    def test_subscribe_pro_payment_failed(self):
        mock_provider = AsyncMock()
        mock_provider.create_payment.return_value = PaymentResult(
            success=False,
            status=PaymentStatus.FAILED,
            message="Payment failed",
        )

        service = SubscriptionService(payment_provider=mock_provider)

        import asyncio

        result = asyncio.run(service.subscribe_pro(user_id=1))

        assert result.success is False
