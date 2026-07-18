"""User schemas."""

from pydantic import BaseModel


class UserUpdate(BaseModel):
    """Foydalanuvchi ma'lumotlarini yangilash."""
    name: str | None = None
    timezone: str | None = None
    notification_prefs: dict | None = None


class UserResponse(BaseModel):
    """Foydalanuvchi javobi."""
    id: str
    telegram_id: str
    name: str
    is_admin: bool
    timezone: str
    created_at: str

    model_config = {"from_attributes": True}
