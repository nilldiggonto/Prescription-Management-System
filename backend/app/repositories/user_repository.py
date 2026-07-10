import uuid
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, *, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        await self._session.flush()
        return user

    async def list_by_role(self, role: UserRole) -> list[User]:
        result = await self._session.execute(select(User).where(User.role == role).order_by(User.created_at))
        return list(result.scalars().all())

    async def count_signups_by_day_since(self, since: datetime) -> dict[date, int]:
        """Used by the admin stats trend chart — doctor signups over time."""
        day = func.date(User.created_at)
        result = await self._session.execute(
            select(day, func.count())
            .where(User.role == UserRole.DOCTOR, User.created_at >= since)
            .group_by(day)
        )
        return dict(result.all())
