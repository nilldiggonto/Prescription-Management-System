from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import generate_token, hash_password, hash_token
from app.models.user import User
from app.repositories.token_repository import EmailVerificationTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailSender


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        email_sender: EmailSender,
    ) -> None:
        self._session = session
        self._settings = settings
        self._email_sender = email_sender
        self._users = UserRepository(session)
        self._tokens = EmailVerificationTokenRepository(session)

    async def register(self, *, email: str, password: str, background_tasks: BackgroundTasks) -> User:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

        user = await self._users.create(email=email, hashed_password=hash_password(password))

        raw_token = generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=self._settings.email_verification_token_expire_hours
        )
        await self._tokens.create(user_id=user.id, token_hash=hash_token(raw_token), expires_at=expires_at)

        await self._session.commit()
        await self._session.refresh(user)

        # Scheduled after the response so registration doesn't block on SMTP latency.
        background_tasks.add_task(self._email_sender.send_verification_email, to=user.email, token=raw_token)

        return user

    async def verify_email(self, *, raw_token: str) -> None:
        token = await self._tokens.get_valid_by_hash(hash_token(raw_token))
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token"
            )

        user = await self._users.get_by_id(token.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token"
            )

        user.is_verified = True
        await self._tokens.mark_used(token)
        await self._session.commit()
