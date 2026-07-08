import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.user import User, UserRole
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import PatientWrite


class PatientService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._patients = PatientRepository(session)

    async def create_patient(self, *, current_user: User, payload: PatientWrite) -> Patient:
        _require_doctor(current_user)

        patient = await self._patients.create(doctor_id=current_user.id, **payload.model_dump())
        await self._session.commit()
        await self._session.refresh(patient)
        return patient

    async def list_my_patients(self, *, current_user: User) -> list[Patient]:
        _require_doctor(current_user)
        return await self._patients.list_for_doctor(current_user.id)

    async def get_my_patient(self, *, current_user: User, patient_id: uuid.UUID) -> Patient:
        _require_doctor(current_user)

        patient = await self._patients.get_by_id_for_doctor(patient_id, current_user.id)
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        return patient


def _require_doctor(user: User) -> None:
    if user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctor accounts have patients")
