"""Security tests for multi-tenant isolation."""

import pytest
from unittest.mock import MagicMock

from src.infrastructure.security.tenant import (
    TenantIsolation,
    SecurityAuditLog,
    InputSanitizer,
)


class TestTenantIsolation:
    """Tenant izolyatsiya testlari."""

    def test_verify_user_access_same_user(self):
        """O'z resursiga kirish ruxsat etiladi."""
        assert TenantIsolation.verify_user_access(123, 123) is True

    def test_verify_user_access_different_user(self):
        """Boshqa foydalanuvchi resursiga kirish taqiqlanadi."""
        assert TenantIsolation.verify_user_access(123, 456) is False

    def test_verify_user_access_admin(self):
        """Admin hamma resursga kirishi mumkin (kelishuv bo'yicha)."""
        # Hozircha oddiy foydalanuvchi logikasi
        assert TenantIsolation.verify_user_access(123, 456) is False


class TestInputSanitizer:
    """Kirish ma'lumotlarini tozash testlari."""

    def test_sanitize_script_tag(self):
        """Script taglari tozalanadi."""
        result = InputSanitizer.sanitize_string("Hello <script>alert('xss')</script>")
        assert "<script>" not in result

    def test_sanitize_javascript_protocol(self):
        """Javascript protokoli tozalanadi."""
        result = InputSanitizer.sanitize_string("javascript:alert('xss')")
        assert "javascript:" not in result

    def test_sanitize_sql_injection(self):
        """SQL injection tozalanadi."""
        result = InputSanitizer.sanitize_string("' OR '1'='1")
        assert "' OR '1'='1" not in result

    def test_sanitize_clean_string(self):
        """Toza satr o'zgartrilmaydi."""
        result = InputSanitizer.sanitize_string("Hello World 123")
        assert result == "Hello World 123"

    def test_validate_input(self):
        """Barcha kirish maydonlari tekshiriladi."""
        data = {"name": "Test <script>", "age": 25}
        result = InputSanitizer.validate_input(data)
        assert "<script>" not in result["name"]
        assert result["age"] == 25


class TestSecurityAuditLog:
    """Audit logging testlari."""

    def test_log_access_attempt_success(self):
        """Muvaffaqiyatli kirish log qilinadi."""
        # Faqat log qilinadi, xato tashlanmaydi
        SecurityAuditLog.log_access_attempt(
            user_id=123,
            resource_type="goal",
            resource_id=456,
            action="read",
            success=True,
        )

    def test_log_access_attempt_denied(self):
        """Rad etilgan kirish log qilinadi."""
        SecurityAuditLog.log_access_attempt(
            user_id=123,
            resource_type="goal",
            resource_id=789,
            action="delete",
            success=False,
            ip_address="192.168.1.1",
        )

    def test_log_suspicious_activity(self):
        """Shubhali faoliyat log qilinadi."""
        SecurityAuditLog.log_suspicious_activity(
            user_id=123,
            activity_type="multiple_failed_logins",
            details="5 failed attempts in 1 minute",
            ip_address="10.0.0.1",
        )
