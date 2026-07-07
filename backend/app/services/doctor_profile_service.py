from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doctor_profile import DoctorProfile
from app.models.user import User, UserRole
from app.repositories.doctor_profile_repository import DoctorProfileRepository
from app.schemas.doctor_profile import DoctorProfileWrite


class DoctorProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._profiles = DoctorProfileRepository(session)

    async def get_my_profile(self, *, current_user: User) -> DoctorProfile:
        _require_doctor(current_user)

        profile = await self._profiles.get_by_user_id(current_user.id)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not set up yet")

        return profile

    async def upsert_my_profile(self, *, current_user: User, payload: DoctorProfileWrite) -> DoctorProfile:
        _require_doctor(current_user)

        profile = await self._profiles.get_by_user_id(current_user.id)
        fields = payload.model_dump()

        if profile is None:
            profile = await self._profiles.create(user_id=current_user.id, **fields)
        else:
            for field, value in fields.items():
                setattr(profile, field, value)

        await self._session.commit()
        await self._session.refresh(profile)
        return profile


def _require_doctor(user: User) -> None:
    if user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only doctor accounts have a doctor profile"
        )
