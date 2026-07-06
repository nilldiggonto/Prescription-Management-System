import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otp import EmailVerificationOTP


class EmailVerificationOTPRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, user_id: uuid.UUID, otp_hash: str, expires_at: datetime) -> EmailVerificationOTP:
        otp = EmailVerificationOTP(user_id=user_id, otp_hash=otp_hash, expires_at=expires_at)
        self._session.add(otp)
        await self._session.flush()
        return otp

    async def get_latest_active_for_user(self, user_id: uuid.UUID) -> EmailVerificationOTP | None:
        """Latest OTP for this user that hasn't been used yet and hasn't expired.
        Attempt-count exhaustion is a separate check left to the caller, since an
        exhausted-but-unexpired OTP should surface a different error message."""
        result = await self._session.execute(
            select(EmailVerificationOTP)
            .where(
                EmailVerificationOTP.user_id == user_id,
                EmailVerificationOTP.used_at.is_(None),
                EmailVerificationOTP.expires_at >= datetime.now(timezone.utc),
            )
            .order_by(EmailVerificationOTP.created_at.desc())
        )
        return result.scalars().first()

    async def increment_attempts(self, otp: EmailVerificationOTP) -> None:
        otp.attempt_count += 1
        await self._session.flush()

    async def mark_used(self, otp: EmailVerificationOTP) -> None:
        otp.used_at = datetime.now(timezone.utc)
        await self._session.flush()