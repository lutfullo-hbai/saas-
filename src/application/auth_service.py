"""Auth service application interface re-exports."""

from src.infrastructure.auth.auth_service import AuthError, AuthService

__all__ = ["AuthError", "AuthService"]
