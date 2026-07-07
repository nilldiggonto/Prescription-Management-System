import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doctor_profile import DoctorProfile


class DoctorProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> DoctorProfile | None:
        result = await self._session.execute(select(DoctorProfile).where(DoctorProfile.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, *, user_id: uuid.UUID, **fields: str | None) -> DoctorProfile:
        profile = DoctorProfile(user_id=user_id, **fields)
        self._session.add(profile)
        await self._session.flush()
        return profile
