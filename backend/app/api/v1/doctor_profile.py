from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession, verify_csrf_token
from app.schemas.doctor_profile import DoctorProfileRead, DoctorProfileWrite
from app.services.doctor_profile_service import DoctorProfileService

router = APIRouter(prefix="/doctor-profile", tags=["doctor-profile"])


@router.get("/me", response_model=DoctorProfileRead)
async def get_my_doctor_profile(current_user: CurrentUser, session: DbSession) -> DoctorProfileRead:
    profile = await DoctorProfileService(session).get_my_profile(current_user=current_user)
    return DoctorProfileRead.model_validate(profile)


@router.put("/me", response_model=DoctorProfileRead, dependencies=[Depends(verify_csrf_token)])
async def upsert_my_doctor_profile(
    payload: DoctorProfileWrite, current_user: CurrentUser, session: DbSession
) -> DoctorProfileRead:
    profile = await DoctorProfileService(session).upsert_my_profile(current_user=current_user, payload=payload)
    return DoctorProfileRead.model_validate(profile)
