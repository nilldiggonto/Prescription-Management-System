import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tokens import EmailVerificationToken


class EmailVerificationTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> EmailVerificationToken:
        token = EmailVerificationToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self._session.add(token)
        await self._session.flush()
        return token

    async def get_valid_by_hash(self, token_hash: str) -> EmailVerificationToken | None:
        result = await self._session.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)
        )
        token = result.scalar_one_or_none()
        if token is None:
            return None
        if token.used_at is not None:
            return None
        if token.expires_at < datetime.now(timezone.utc):
            return None
        return token

    async def mark_used(self, token: EmailVerificationToken) -> None:
        token.used_at = datetime.now(timezone.utc)
        await self._session.flush()
