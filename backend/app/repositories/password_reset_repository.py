import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_otp import PasswordResetOTP


class PasswordResetOTPRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, user_id: uuid.UUID, otp_hash: str, expires_at: datetime) -> PasswordResetOTP:
        otp = PasswordResetOTP(user_id=user_id, otp_hash=otp_hash, expires_at=expires_at)
        self._session.add(otp)
        await self._session.flush()
        return otp

    async def get_latest_active_for_user(self, user_id: uuid.UUID) -> PasswordResetOTP | None:
        """Latest OTP for this user that hasn't been used yet and hasn't expired.
        Attempt-count exhaustion is a separate check left to the caller, since an
        exhausted-but-unexpired OTP should surface a different error message."""
        result = await self._session.execute(
            select(PasswordResetOTP)
            .where(
                PasswordResetOTP.user_id == user_id,
                PasswordResetOTP.used_at.is_(None),
                PasswordResetOTP.expires_at >= datetime.now(timezone.utc),
            )
            .order_by(PasswordResetOTP.created_at.desc())
        )
        return result.scalars().first()

    async def increment_attempts(self, otp: PasswordResetOTP) -> None:
        otp.attempt_count += 1
        await self._session.flush()

    async def mark_used(self, otp: PasswordResetOTP) -> None:
        otp.used_at = datetime.now(timezone.utc)
        await self._session.flush()
