"""Auth service implementation — infrastructure layer."""

from datetime import timedelta
from uuid import UUID

from src.utils.datetime_utils import utc_now

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.infrastructure.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from src.infrastructure.auth.password import hash_password, verify_password
from src.infrastructure.db.models.user import UserModel, UserSessionModel

logger = get_logger(__name__)


class AuthError(Exception):
    """Auth xatosi."""

    pass


class AuthService:
    """Autentifikatsiya xizmati."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(
        self,
        email: str,
        password: str,
        name: str,
        ip_address: str | None = None,
        telegram_id: int | None = None,
    ) -> dict:
        """Ro'yxatdan o'tish."""
        existing = await self._get_user_by_email(email)
        if existing:
            raise AuthError("Bu email allaqachon ro'yxatdan o'tgan")

        user = UserModel(
            email=email,
            password_hash=hash_password(password),
            name=name,
            is_verified=False,
            telegram_id=telegram_id,
        )
        self.session.add(user)
        await self.session.flush()

        logger.info("user_registered", user_id=str(user.id), email=email)

        return await self._create_tokens(user, ip_address, telegram_id)

    async def login(
        self, email: str, password: str, ip_address: str | None = None
    ) -> dict:
        """Kirish."""
        user = await self._get_user_by_email(email)
        if user is None or not user.password_hash:
            raise AuthError("Email yoki parol noto'g'ri")

        if not verify_password(password, user.password_hash):
            logger.warning("login_failed", email=email, ip=ip_address)
            raise AuthError("Email yoki parol noto'g'ri")

        if not user.is_active:
            raise AuthError("Hisob faol emas")

        user.last_login_at = utc_now()
        user.last_login_ip = ip_address
        await self.session.flush()

        logger.info("user_logged_in", user_id=str(user.id), email=email)

        return await self._create_tokens(user, ip_address, user.telegram_id)

    async def refresh(self, refresh_token: str, ip_address: str | None = None) -> dict:
        """Refresh token rotation."""
        payload = decode_refresh_token(refresh_token)
        if payload is None:
            raise AuthError("Yaroqsiz refresh token")

        user_id = payload["user_id"]
        jti = payload["jti"]

        session = await self._get_session_by_jti(jti)
        if session is None or not session.is_active:
            raise AuthError("Sessiya topilmadi yoki bekor qilingan")

        if session.expires_at < utc_now():
            session.is_active = False
            await self.session.flush()
            raise AuthError("Sessiya muddati tugagan")

        session.is_active = False
        await self.session.flush()

        user = await self._get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthError("Foydalanuvchi topilmadi yoki faol emas")

        logger.info(
            "token_refreshed",
            user_id=str(user_id),
            old_jti=jti,
        )

        return await self._createtokens(user, ip_address, user.telegram_id)

    async def logout(self, refresh_token: str) -> None:
        """Bitta sessiyadan chiqish."""
        payload = decode_refresh_token(refresh_token)
        if payload is None:
            return

        jti = payload["jti"]
        session = await self._get_session_by_jti(jti)
        if session:
            session.is_active = False
            await self.session.flush()
            logger.info("session_revoked", user_id=str(payload["user_id"]), jti=jti)

    async def logout_all(self, user_id: UUID) -> None:
        """Barcha sessiyalardan chiqish."""
        await self.session.execute(
            update(UserSessionModel)
            .where(
                UserSessionModel.user_id == user_id,
                UserSessionModel.is_active,
            )
            .values(is_active=False)
        )
        await self.session.flush()
        logger.info("all_sessions_revoked", user_id=str(user_id))

    async def get_sessions(
        self, user_id: UUID, current_jti: str | None = None
    ) -> list[dict]:
        """Foydalanuvchi sessiyalarini olish."""
        result = await self.session.execute(
            select(UserSessionModel).where(
                UserSessionModel.user_id == user_id,
                UserSessionModel.is_active,
            )
        )
        sessions = result.scalars().all()

        return [
            {
                "id": str(s.id),
                "device_info": s.device_info,
                "ip_address": s.ip_address,
                "created_at": s.created_at.isoformat() if s.created_at else "",
                "last_used_at": s.last_used_at.isoformat() if s.last_used_at else "",
                "is_current": s.refresh_token_jti == current_jti,
            }
            for s in sessions
        ]

    async def _createtokens(
        self,
        user: UserModel,
        ip_address: str | None = None,
        telegram_id: int | None = None,
    ) -> dict:
        """Tokenlar yaratish va sessiya saqlash."""
        access_token = create_access_token(user.id, user.email, telegram_id)
        refresh_token = create_refresh_token(user.id, user.email, telegram_id)

        payload = decode_refresh_token(refresh_token)
        if payload is None:
            raise AuthError("Token yaratishda xatolik")

        session = UserSessionModel(
            user_id=user.id,
            refresh_token_jti=payload["jti"],
            ip_address=ip_address,
            is_active=True,
            expires_at=utc_now() + timedelta(days=30),
        )
        self.session.add(session)
        await self.session.flush()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,
        }

    async def _get_user_by_email(self, email: str) -> UserModel | None:
        """Email bo'yicha foydalanuvchi topish."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: UUID) -> UserModel | None:
        """ID bo'yicha foydalanuvchi topish."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_session_by_jti(self, jti: str) -> UserSessionModel | None:
        """JTI bo'yicha sessiya topish."""
        result = await self.session.execute(
            select(UserSessionModel).where(UserSessionModel.refresh_token_jti == jti)
        )
        return result.scalar_one_or_none()
