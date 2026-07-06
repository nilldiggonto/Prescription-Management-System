from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import generate_otp, hash_password, hash_secret
from app.models.user import User
from app.repositories.otp_repository import EmailVerificationOTPRepository
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
        self._otps = EmailVerificationOTPRepository(session)

    async def register(self, *, email: str, password: str, background_tasks: BackgroundTasks) -> User:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

        user = await self._users.create(email=email, hashed_password=hash_password(password))

        raw_otp = generate_otp()
        expire_minutes = self._settings.email_verification_otp_expire_minutes
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        await self._otps.create(user_id=user.id, otp_hash=hash_secret(raw_otp), expires_at=expires_at)

        await self._session.commit()
        await self._session.refresh(user)

        # Scheduled after the response so registration doesn't block on SMTP latency.
        background_tasks.add_task(
            self._email_sender.send_verification_otp, to=user.email, otp=raw_otp, expire_minutes=expire_minutes
        )

        return user

    async def verify_email(self, *, email: str, otp: str) -> None:
        user = await self._users.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or OTP")

        if user.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already verified")

        otp_record = await self._otps.get_latest_active_for_user(user.id)
        if otp_record is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP. Please request a new code."
            )

        if otp_record.attempt_count >= self._settings.email_verification_otp_max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many failed attempts. Please request a new code.",
            )

        if hash_secret(otp) != otp_record.otp_hash:
            await self._otps.increment_attempts(otp_record)
            await self._session.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code")

        user.is_verified = True
        await self._otps.mark_used(otp_record)
        await self._session.commit()
