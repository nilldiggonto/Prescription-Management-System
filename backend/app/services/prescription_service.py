import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.user import User, UserRole
from app.repositories.doctor_profile_repository import DoctorProfileRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.prescription_repository import PrescriptionRepository
from app.schemas.prescription import PrescriptionCreate


class PrescriptionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._prescriptions = PrescriptionRepository(session)
        self._patients = PatientRepository(session)
        self._doctor_profiles = DoctorProfileRepository(session)

    async def create_prescription(self, *, current_user: User, payload: PrescriptionCreate) -> Prescription:
        _require_doctor(current_user)

        doctor_profile = await self._doctor_profiles.get_by_user_id(current_user.id)
        if doctor_profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Set up your doctor profile before creating a prescription",
            )

        patient = await self._resolve_patient(current_user=current_user, payload=payload)

        prescription = await self._prescriptions.create(
            doctor_id=current_user.id,
            patient=patient,
            diagnosis=payload.diagnosis,
            advice=payload.advice,
            follow_up_date=payload.follow_up_date,
            medicines=[medicine.model_dump() for medicine in payload.medicines],
        )
        # Not calling session.refresh() here: it would expire the `patient`/`medicines`
        # relationships we just attached in-memory, forcing a lazy reload on next access —
        # which async SQLAlchemy can't do implicitly. expire_on_commit=False (see
        # core/database.py) already keeps every attribute intact post-commit.
        await self._session.commit()
        return prescription

    async def _resolve_patient(self, *, current_user: User, payload: PrescriptionCreate) -> Patient:
        if payload.patient_id is not None:
            patient = await self._patients.get_by_id_for_doctor(payload.patient_id, current_user.id)
            if patient is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
            return patient

        assert payload.new_patient is not None  # enforced by PrescriptionCreate validator
        return await self._patients.create(doctor_id=current_user.id, **payload.new_patient.model_dump())

    async def list_my_prescriptions(self, *, current_user: User) -> list[Prescription]:
        _require_doctor(current_user)
        return await self._prescriptions.list_for_doctor(current_user.id)

    async def get_my_prescription(self, *, current_user: User, prescription_id: uuid.UUID) -> Prescription:
        _require_doctor(current_user)

        prescription = await self._prescriptions.get_by_id_for_doctor(prescription_id, current_user.id)
        if prescription is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")

        return prescription


def _require_doctor(user: User) -> None:
    if user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctor accounts have prescriptions")
