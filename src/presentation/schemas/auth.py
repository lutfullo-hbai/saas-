"""Auth schemas — Pydantic models for auth endpoints."""

import re

from pydantic import BaseModel, field_validator


class RegisterRequest(BaseModel):
    """Ro'yxatdan o'tish so'rovi."""

    email: str
    password: str
    name: str
    telegram_id: int | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Noto'g'ri email format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Parol kamida 8 ta belgi bo'lishi kerak")
        if len(v) > 128:
            raise ValueError("Parol 128 ta belgidan oshmasligi kerak")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Ism kamida 2 ta belgi bo'lishi kerak")
        return v


class LoginRequest(BaseModel):
    """Kirish so'rovi."""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    """JWT token javobi."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token so'rovi."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Tizimdan chiqish so'rovi."""

    refresh_token: str


class LogoutAllRequest(BaseModel):
    """Barcha sessiyalardan chiqish so'rovi."""

    pass


class PasswordChangeRequest(BaseModel):
    """Parol o'zgartirish so'rovi."""

    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Yangi parol kamida 8 ta belgi bo'lishi kerak")
        return v


class UserResponse(BaseModel):
    """Foydalanuvchi javobi."""

    id: str
    email: str
    name: str
    role: str
    is_active: bool
    is_verified: bool
    timezone: str
    created_at: str

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    """Sessiya javobi."""

    id: str
    device_info: str | None
    ip_address: str | None
    created_at: str
    last_used_at: str
    is_current: bool = False
