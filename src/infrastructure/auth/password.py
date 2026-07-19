"""Password hashing service — Argon2id."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
)


def hash_password(password: str) -> str:
    """Parolni Argon2id bilan hash qilish."""
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Parolni tekshirish."""
    try:
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def needs_rehash(password_hash: str) -> bool:
    """Hash qayta hashlash kerakligini tekshirish (parametrlar o'zgargan bo'lsa)."""
    return ph.check_needs_rehash(password_hash)
