"""Authentication API endpoints — email-based auth."""


from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.auth_service import AuthError, AuthService
from src.infrastructure.db.models.user import UserModel
from src.presentation.api.dependencies import (
    CurrentUser,
    get_client_ip,
    get_current_user,
    get_db,
)
from src.presentation.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    RegisterRequest,
    SessionResponse,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequest,
    req: Request,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Ro'yxatdan o'tish — email + parol bilan."""
    ip_address = get_client_ip(req)
    service = AuthService(session)

    try:
        result = await service.register(
            email=request.email,
            password=request.password,
            name=request.name,
            ip_address=ip_address,
            telegram_id=request.telegram_id,
        )
        await session.commit()
        return TokenResponse(**result)
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    req: Request,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Kirish — email + parol bilan."""
    ip_address = get_client_ip(req)
    service = AuthService(session)

    try:
        result = await service.login(
            email=request.email,
            password=request.password,
            ip_address=ip_address,
        )
        await session.commit()
        return TokenResponse(**result)
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from None


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    req: Request,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh token rotation — eski token bekor qilinadi, yangisi beriladi."""
    ip_address = get_client_ip(req)
    service = AuthService(session)

    try:
        result = await service.refresh(
            refresh_token=request.refresh_token,
            ip_address=ip_address,
        )
        await session.commit()
        return TokenResponse(**result)
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from None


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: LogoutRequest,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Bitta sessiyadan chiqish."""
    service = AuthService(session)
    await service.logout(request.refresh_token)
    await session.commit()


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Barcha sessiyalardan chiqish."""
    service = AuthService(session)
    await service.logout_all(current_user.user_id)
    await session.commit()


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Hozirgi foydalanuvchi ma'lumotlari."""
    result = await session.execute(
        select(UserModel).where(UserModel.id == current_user.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi",
        )
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        timezone=user.timezone,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )


@router.get("/sessions", response_model=list[SessionResponse])
async def get_sessions(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[SessionResponse]:
    """Foydalanuvchi sessiyalarini ko'rish."""
    service = AuthService(session)
    sessions = await service.get_sessions(current_user.user_id)
    return [SessionResponse(**s) for s in sessions]


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: PasswordChangeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Parolni o'zgartirish."""
    from src.infrastructure.auth.password import hash_password, verify_password

    result = await session.execute(
        select(UserModel).where(UserModel.id == current_user.user_id)
    )
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi",
        )

    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joriy parol noto'g'ri",
        )

    user.password_hash = hash_password(request.new_password)
    await session.commit()
