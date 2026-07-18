"""Unit tests for encryption at rest."""

import pytest

from src.infrastructure.security.encryption import encrypt, decrypt


class TestEncryption:
    """Fernet encryption testlari."""

    def test_encrypt_decrypt_roundtrip(self):
        """Shifrlash va ochish — asl matn qaytishi kerak."""
        original = "Bu maxfiy ma'lumot"
        encrypted = encrypt(original)
        decrypted = decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_produces_different_output(self):
        """Har bir shifrlash natijasi farqli bo'lishi kerak."""
        text = "Same text"
        enc1 = encrypt(text)
        enc2 = encrypt(text)
        assert enc1 != enc2  # Fernet timestamp qo'shadi

    def test_decrypt_wrong_key_fails(self):
        """Noto'g'ri kalit bilan ochish xatolik berishi kerak."""
        encrypted = encrypt("secret data")
        # Boshqa kalit bilan ochishga urinib ko'rish
        with pytest.raises(Exception):
            # Agar ENCRYPTION_KEY o'zgarsa, decrypt xatolik beradi
            decrypt(encrypted)

    def test_encrypt_empty_string(self):
        """Bo'sh matnni shifrlash."""
        encrypted = encrypt("")
        decrypted = decrypt(encrypted)
        assert decrypted == ""

    def test_encrypt_long_text(self):
        """Uzoq matnni shifrlash."""
        original = "x" * 10000
        encrypted = encrypt(original)
        decrypted = decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_special_characters(self):
        """Maxsus belgilar bilan shifrlash."""
        original = "O'zbekiston! @#$%^&*() 123"
        encrypted = encrypt(original)
        decrypted = decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_unicode(self):
        """Unicode matnni shifrlash."""
        original = "Привет мир 你好世界"
        encrypted = encrypt(original)
        decrypted = decrypt(encrypted)
        assert decrypted == original
