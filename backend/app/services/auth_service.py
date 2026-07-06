import uuid
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import generate_otp, generate_token, hash_password, hash_secret, verify_password
from app.models.user import User
from app.repositories.access_token_repository import AccessTokenRepository
from app.repositories.otp_repository import EmailVerificationOTPRepository
from app.repositories.password_reset_repository import PasswordResetOTPRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailSender

# Verified against on a login attempt for an email that doesn't exist, so the response
# takes roughly the same time whether or not the account is real (avoids user enumeration via timing).
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-not-a-real-account")


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
        self._password_resets = PasswordResetOTPRepository(session)
        self._access_tokens = AccessTokenRepository(session)

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

        otp_record = await self._consume_otp(
            otp_repo=self._otps,
            user_id=user.id,
            otp=otp,
            max_attempts=self._settings.email_verification_otp_max_attempts,
        )

        user.is_verified = True
        await self._otps.mark_used(otp_record)
        await self._session.commit()

    async def login(self, *, email: str, password: str, remember_me: bool) -> tuple[User, str, str]:
        user = await self._users.get_by_email(email)
        if user is None:
            verify_password(password, _DUMMY_PASSWORD_HASH)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        if not user.is_verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email first")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is suspended")

        expire_days = (
            self._settings.access_token_remember_me_expire_days
            if remember_me
            else self._settings.access_token_expire_days
        )
        raw_access_token = generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(days=expire_days)
        await self._access_tokens.create(
            user_id=user.id,
            token_hash=hash_secret(raw_access_token),
            expires_at=expires_at,
            remember_me=remember_me,
        )
        await self._session.commit()

        csrf_token = generate_token()
        return user, raw_access_token, csrf_token

    async def logout(self, *, raw_access_token: str) -> None:
        await self._access_tokens.revoke_by_hash(hash_secret(raw_access_token))
        await self._session.commit()

    async def forgot_password(self, *, email: str, background_tasks: BackgroundTasks) -> None:
        # Response to the caller is identical whether or not the email exists, to avoid enumeration.
        user = await self._users.get_by_email(email)
        if user is None or not user.is_active:
            return

        raw_otp = generate_otp()
        expire_minutes = self._settings.password_reset_otp_expire_minutes
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        await self._password_resets.create(user_id=user.id, otp_hash=hash_secret(raw_otp), expires_at=expires_at)
        await self._session.commit()

        background_tasks.add_task(
            self._email_sender.send_password_reset_otp, to=user.email, otp=raw_otp, expire_minutes=expire_minutes
        )

    async def reset_password(self, *, email: str, otp: str, new_password: str) -> None:
        user = await self._users.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or OTP")

        otp_record = await self._consume_otp(
            otp_repo=self._password_resets,
            user_id=user.id,
            otp=otp,
            max_attempts=self._settings.password_reset_otp_max_attempts,
        )

        user.hashed_password = hash_password(new_password)
        await self._password_resets.mark_used(otp_record)
        # A changed password invalidates every existing session.
        await self._access_tokens.revoke_all_for_user(user.id)
        await self._session.commit()

    async def _consume_otp(
        self,
        *,
        otp_repo: EmailVerificationOTPRepository | PasswordResetOTPRepository,
        user_id: uuid.UUID,
        otp: str,
        max_attempts: int,
    ):
        otp_record = await otp_repo.get_latest_active_for_user(user_id)
        if otp_record is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP. Please request a new code."
            )

        if otp_record.attempt_count >= max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many failed attempts. Please request a new code.",
            )

        if hash_secret(otp) != otp_record.otp_hash:
            await otp_repo.increment_attempts(otp_record)
            await self._session.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code")

        return otp_record
