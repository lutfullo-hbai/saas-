"""Encryption at rest — maxfiy ma'lumotlarni shifrlash.

Foydalanish:
    from src.infrastructure.security.encryption import encrypt_field, decrypt_field

    encrypted = encrypt_field("Goal description")
    original = decrypt_field(encrypted)

Konfiguratsiya:
    .env faylida ENCRYPTION_KEY aniqlanishi kerak.
    Agar yo'q bo'lsa, avtomatik generatsiya qilinadi (dev uchun).
    Production'da doim ENCRYPTION_KEY o'rnatilishi shart!
"""

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

from src.config.logging import get_logger
from src.config.settings import settings

logger = get_logger(__name__)

# Fernet uchun kalit 32 base64-encoded byte bo'lishi kerak
_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    """Fernet instansiyasini olish (lazy initialization)."""
    global _fernet
    if _fernet is not None:
        return _fernet

    encryption_key = getattr(settings, "encryption_key", None)

    if not encryption_key:
        # Dev muhiti uchun avtomatik kalit generatsiya qilish
        # Production'da bu ishlatilmasligi kerak!
        if settings.app_env == "production":
            raise RuntimeError(
                "ENCRYPTION_KEY production muhitida majburiy! "
                ".env faylida ENCRYPTION_KEY aniqlang."
            )
        logger.warning("encryption_key_not_set_using_dev_fallback")
        encryption_key = "dev-only-key-do-not-use-in-production"

    # Kalitni 32 baytga normalize qilish
    key_bytes = hashlib.sha256(encryption_key.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    _fernet = Fernet(fernet_key)
    return _fernet


def encrypt_field(plaintext: str | None) -> str | None:
    """Matnni shifrlash.

    Args:
        plaintext: Shifrlanadigan matn.

    Returns:
        Shifrlangan matn (base64 formatida) yoki None.
    """
    if not plaintext:
        return plaintext

    try:
        fernet = _get_fernet()
        encrypted = fernet.encrypt(plaintext.encode("utf-8"))
        return encrypted.decode("utf-8")
    except Exception as e:
        logger.error("encryption_failed", error=str(e))
        raise


def decrypt_field(ciphertext: str | None) -> str | None:
    """Shifrlangan matnni ochish.

    Args:
        ciphertext: Shifrlangan matn.

    Returns:
        Ochilgan matn yoki None.
    """
    if not ciphertext:
        return ciphertext

    try:
        fernet = _get_fernet()
        decrypted = fernet.decrypt(ciphertext.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken:
        logger.warning("decryption_invalid_token")
        # Token noto'g'ri — bu shifrlanmagan matn bo'lishi mumkin
        # (eski ma'lumotlar migration qilinmagan)
        return ciphertext
    except Exception as e:
        logger.error("decryption_failed", error=str(e))
        raise


def is_encrypted(value: str | None) -> bool:
    """Matn shifrlanganligini tekshirish.

    Fernet shifrlangan matn '.' belgisi bilan ajratilgan
    3 ta qismdan iborat: version.timestamp.ciphertext
    """
    if not value:
        return False
    try:
        parts = value.split(".")
        return len(parts) == 3 and parts[0] == "gAAAAA"
    except Exception:
        return False
