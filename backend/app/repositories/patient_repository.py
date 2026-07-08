import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient


class PatientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, doctor_id: uuid.UUID, **fields: str | int | None) -> Patient:
        patient = Patient(doctor_id=doctor_id, **fields)
        self._session.add(patient)
        await self._session.flush()
        return patient

    async def get_by_id_for_doctor(self, patient_id: uuid.UUID, doctor_id: uuid.UUID) -> Patient | None:
        result = await self._session.execute(
            select(Patient).where(Patient.id == patient_id, Patient.doctor_id == doctor_id)
        )
        return result.scalar_one_or_none()

    async def list_for_doctor(self, doctor_id: uuid.UUID) -> list[Patient]:
        result = await self._session.execute(
            select(Patient).where(Patient.doctor_id == doctor_id).order_by(Patient.full_name)
        )
        return list(result.scalars().all())
