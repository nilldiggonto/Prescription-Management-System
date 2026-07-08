import uuid

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession, verify_csrf_token
from app.schemas.patient import PatientRead, PatientWrite
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientRead, status_code=201, dependencies=[Depends(verify_csrf_token)])
async def create_patient(payload: PatientWrite, current_user: CurrentUser, session: DbSession) -> PatientRead:
    patient = await PatientService(session).create_patient(current_user=current_user, payload=payload)
    return PatientRead.model_validate(patient)


@router.get("", response_model=list[PatientRead])
async def list_patients(current_user: CurrentUser, session: DbSession) -> list[PatientRead]:
    patients = await PatientService(session).list_my_patients(current_user=current_user)
    return [PatientRead.model_validate(patient) for patient in patients]


@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(patient_id: uuid.UUID, current_user: CurrentUser, session: DbSession) -> PatientRead:
    patient = await PatientService(session).get_my_patient(current_user=current_user, patient_id=patient_id)
    return PatientRead.model_validate(patient)
