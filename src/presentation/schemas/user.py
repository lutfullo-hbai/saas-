"""User schemas."""

from pydantic import BaseModel


class UserUpdate(BaseModel):
    """Foydalanuvchi ma'lumotlarini yangilash."""

    name: str | None = None
    timezone: str | None = None
    notification_prefs: dict | None = None
    role: str | None = None


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
