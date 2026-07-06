import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.access_token import AccessToken


class AccessTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime, remember_me: bool
    ) -> AccessToken:
        access_token = AccessToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at, remember_me=remember_me
        )
        self._session.add(access_token)
        await self._session.flush()
        return access_token

    async def get_valid_by_hash(self, token_hash: str) -> AccessToken | None:
        result = await self._session.execute(
            select(AccessToken).where(
                AccessToken.token_hash == token_hash,
                AccessToken.revoked_at.is_(None),
                AccessToken.expires_at >= datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def revoke_by_hash(self, token_hash: str) -> None:
        await self._session.execute(
            update(AccessToken)
            .where(AccessToken.token_hash == token_hash, AccessToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(
            update(AccessToken)
            .where(AccessToken.user_id == user_id, AccessToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self._session.flush()
