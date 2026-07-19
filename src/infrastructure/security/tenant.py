"""Multi-tenant security audit and isolation."""

from functools import wraps
from typing import Any, Callable

from fastapi import Request, HTTPException, status

from src.config.logging import get_logger

logger = get_logger(__name__)


class TenantIsolation:
    """Multi-tenant xavfsizlik izolyatsiyasi."""

    @staticmethod
    def verify_user_access(resource_user_id: int, current_user_id: int) -> bool:
        """Foydalanuvchi resursga kirish huqugini tekshirish."""
        if resource_user_id != current_user_id:
            logger.warning(
                f"Access denied: user {current_user_id} tried to access "
                f"resource of user {resource_user_id}"
            )
            return False
        return True

    @staticmethod
    def filter_query_by_user(query, user_id: int):
        """So'rovni foydalanuvchi bo'yicha filtrlash."""
        return query.filter(user_id=user_id)

    @staticmethod
    def validate_tenant_context(request: Request, resource_user_id: int) -> None:
        """Tenant kontekstini tekshirish."""
        current_user = getattr(request.state, "user", None)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        if not TenantIsolation.verify_user_access(
            resource_user_id, current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only access your own resources",
            )


def require_tenant_access(func: Callable) -> Callable:
    """Tenant access decorator."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if not request:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if not request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request object not found",
            )

        return await func(*args, **kwargs)
    return wrapper


class SecurityAuditLog:
    """Xavfsizlik audit logging."""

    @staticmethod
    def log_access_attempt(
        user_id: int,
        resource_type: str,
        resource_id: Any,
        action: str,
        success: bool,
        ip_address: str | None = None,
    ) -> None:
        """Kirish urinishini log qilish."""
        status_text = "SUCCESS" if success else "DENIED"
        logger.info(
            f"SECURITY_AUDIT: [{status_text}] "
            f"user={user_id} resource={resource_type}:{resource_id} "
            f"action={action} ip={ip_address}"
        )

    @staticmethod
    def log_data_access(
        user_id: int,
        data_type: str,
        record_count: int,
        filters: dict | None = None,
    ) -> None:
        """Ma'lumot kirishini log qilish."""
        logger.info(
            f"DATA_ACCESS: user={user_id} type={data_type} "
            f"records={record_count} filters={filters}"
        )

    @staticmethod
    def log_suspicious_activity(
        user_id: int,
        activity_type: str,
        details: str,
        ip_address: str | None = None,
    ) -> None:
        """Shubhali faoliyatni log qilish."""
        logger.warning(
            f"SUSPICIOUS_ACTIVITY: user={user_id} "
            f"type={activity_type} details={details} ip={ip_address}"
        )


class InputSanitizer:
    """Kirish ma'lumotlarini tozalash."""

    DANGEROUS_PATTERNS = [
        "<script",
        "javascript:",
        "onerror=",
        "onload=",
        "onmouseover=",
        "' OR '1'='1",
        "'; DROP TABLE",
        "UNION SELECT",
    ]

    @staticmethod
    def sanitize_string(value: str) -> str:
        """Xavfli belgilarni tozalash."""
        if not isinstance(value, str):
            return value

        sanitized = value
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            if pattern.lower() in sanitized.lower():
                logger.warning(f"Dangerous pattern detected: {pattern}")
                sanitized = sanitized.replace(pattern, "")

        return sanitized.strip()

    @staticmethod
    def validate_input(data: dict) -> dict:
        """Barcha kirish maydonlarini tekshirish."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value)
            else:
                sanitized[key] = value
        return sanitized
