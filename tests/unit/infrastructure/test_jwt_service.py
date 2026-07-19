"""Unit tests for JWT service with refresh token."""

from uuid import uuid4

from src.infrastructure.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)


class TestJWTService:
    """JWT service testlari."""

    def test_create_access_token_returns_string(self):
        """Access token — string qaytarishi kerak."""
        token = create_access_token(uuid4(), "test@disipl.test")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_valid(self):
        """Yaroqli access token decode qilish."""
        user_id = uuid4()
        email = "test@disipl.test"
        token = create_access_token(user_id, email)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["email"] == email

    def test_decode_access_token_invalid(self):
        """Yaroqsiz access token — None qaytarishi kerak."""
        payload = decode_access_token("invalid.token.here")
        assert payload is None

    def test_create_refresh_token_returns_string(self):
        """Refresh token — string qaytarishi kerak."""
        token = create_refresh_token(uuid4(), "test@disipl.test")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_refresh_token_valid(self):
        """Yaroqli refresh token decode qilish."""
        user_id = uuid4()
        email = "test@disipl.test"
        token = create_refresh_token(user_id, email)
        payload = decode_refresh_token(token)
        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["email"] == email
        assert "jti" in payload

    def test_decode_refresh_token_invalid(self):
        """Yaroqsiz refresh token — None."""
        payload = decode_refresh_token("invalid.token.here")
        assert payload is None

    def test_access_token_cannot_be_used_as_refresh(self):
        """Access token refresh sifatida ishlatilmasligi kerak."""
        token = create_access_token(uuid4(), "test@disipl.test")
        payload = decode_refresh_token(token)
        assert payload is None

    def test_refresh_token_cannot_be_used_as_access(self):
        """Refresh token access sifatida ishlatilmasligi kerak."""
        token = create_refresh_token(uuid4(), "test@disipl.test")
        payload = decode_access_token(token)
        assert payload is None

    def test_refresh_token_has_unique_jti(self):
        """Har bir refresh token noyob JTI ga ega."""
        token1 = create_refresh_token(uuid4(), "test@disipl.test")
        token2 = create_refresh_token(uuid4(), "test@disipl.test")
        payload1 = decode_refresh_token(token1)
        payload2 = decode_refresh_token(token2)
        assert payload1["jti"] != payload2["jti"]
