from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.cookies import ACCESS_TOKEN_COOKIE, CSRF_TOKEN_COOKIE
from app.core.database import get_db
from app.core.security import hash_secret
from app.models.user import User, UserRole
from app.repositories.access_token_repository import AccessTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.email_service import EmailSender, get_email_sender

DbSession = Annotated[AsyncSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]
EmailSenderDep = Annotated[EmailSender, Depends(get_email_sender)]


def get_auth_service(
    session: DbSession,
    settings: AppSettings,
    email_sender: EmailSenderDep,
) -> AuthService:
    return AuthService(session=session, settings=settings, email_sender=email_sender)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(request: Request, session: DbSession) -> User:
    raw_token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if raw_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    access_token = await AccessTokenRepository(session).get_valid_by_hash(hash_secret(raw_token))
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = await UserRepository(session).get_by_id(access_token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_admin(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]


def verify_csrf_token(request: Request) -> None:
    cookie_value = request.cookies.get(CSRF_TOKEN_COOKIE)
    header_value = request.headers.get("x-csrf-token")
    if not cookie_value or not header_value or cookie_value != header_value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token missing or invalid")
