import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.prescription_medicine import PrescriptionMedicine


class PrescriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        doctor_id: uuid.UUID,
        patient: Patient,
        diagnosis: str | None,
        advice: str | None,
        follow_up_date: date | None,
        medicines: list[dict[str, str | None]],
    ) -> Prescription:
        # Assigning the `patient` relationship (rather than just `patient_id`) means the object
        # is already attached in-memory, so callers can read `prescription.patient` right after
        # this without a second query — relevant because async relationship access can't lazy-load.
        prescription = Prescription(
            doctor_id=doctor_id,
            patient=patient,
            diagnosis=diagnosis,
            advice=advice,
            follow_up_date=follow_up_date,
            medicines=[
                PrescriptionMedicine(**medicine, sort_order=index) for index, medicine in enumerate(medicines)
            ],
        )
        self._session.add(prescription)
        await self._session.flush()
        return prescription

    async def get_by_id_for_doctor(self, prescription_id: uuid.UUID, doctor_id: uuid.UUID) -> Prescription | None:
        result = await self._session.execute(
            select(Prescription).where(Prescription.id == prescription_id, Prescription.doctor_id == doctor_id)
        )
        return result.scalar_one_or_none()

    async def list_for_doctor(self, doctor_id: uuid.UUID) -> list[Prescription]:
        result = await self._session.execute(
            select(Prescription).where(Prescription.doctor_id == doctor_id).order_by(Prescription.created_at.desc())
        )
        return list(result.scalars().all())
