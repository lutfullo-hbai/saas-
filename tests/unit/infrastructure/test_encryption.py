"""Unit tests for encryption at rest."""

import pytest

from src.infrastructure.security.encryption import encrypt_field, decrypt_field


class TestEncryption:
    """Fernet encryption testlari."""

    def test_encrypt_decrypt_roundtrip(self):
        """Shifrlash va ochish — asl matn qaytishi kerak."""
        original = "Bu maxfiy ma'lumot"
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        assert decrypted == original

    def test_encrypt_produces_different_output(self):
        """Har bir shifrlash natijasi farqli bo'lishi kerak."""
        text = "Same text"
        enc1 = encrypt_field(text)
        enc2 = encrypt_field(text)
        assert enc1 != enc2  # Fernet timestamp qo'shadi

    def test_decrypt_with_different_key_returns_ciphertext(self):
        """Noto'g'ri kalit bilan ochish — asl shifrlangan matn qaytariladi.

        decrypt_field() InvalidToken xatosini tutib, asl matnni qaytaradi
        (migration uchun mo'ljallangan).
        """
        import base64
        import hashlib

        from cryptography.fernet import Fernet

        import src.infrastructure.security.encryption as enc_module

        encrypted = encrypt_field("secret data")

        # Hozirgi _fernet ni vaqtincha saqlash
        original_fernet = enc_module._fernet
        try:
            # Fernet ni tozalash va boshqa kalit bilan yaratish
            enc_module._fernet = None
            different_key = hashlib.sha256(b"different-key-12345").digest()
            fernet_key = base64.urlsafe_b64encode(different_key)
            enc_module._fernet = Fernet(fernet_key)

            # Noto'g'ri kalit bilan ochish — asl matn qaytarilishi kerak
            result = decrypt_field(encrypted)
            assert result == encrypted  # InvalidToken catch qilinadi, asl qaytariladi
        finally:
            enc_module._fernet = original_fernet

    def test_encrypt_empty_string(self):
        """Bo'sh matnni shifrlash."""
        encrypted = encrypt_field("")
        decrypted = decrypt_field(encrypted)
        assert decrypted == ""

    def test_encrypt_long_text(self):
        """Uzoq matnni shifrlash."""
        original = "x" * 10000
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        assert decrypted == original

    def test_encrypt_special_characters(self):
        """Maxsus belgilar bilan shifrlash."""
        original = "O'zbekiston! @#$%^&*() 123"
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        assert decrypted == original

    def test_encrypt_unicode(self):
        """Unicode matnni shifrlash."""
        original = "Привет мир 你好世界"
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        assert decrypted == original
