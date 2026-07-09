import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.api.deps import CurrentUser, DbSession, verify_csrf_token
from app.repositories.doctor_profile_repository import DoctorProfileRepository
from app.schemas.prescription import PrescriptionCreate, PrescriptionRead
from app.services.pdf_service import generate_prescription_pdf
from app.services.prescription_service import PrescriptionService

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


@router.post("", response_model=PrescriptionRead, status_code=201, dependencies=[Depends(verify_csrf_token)])
async def create_prescription(
    payload: PrescriptionCreate, current_user: CurrentUser, session: DbSession
) -> PrescriptionRead:
    prescription = await PrescriptionService(session).create_prescription(current_user=current_user, payload=payload)
    return PrescriptionRead.model_validate(prescription)


@router.get("", response_model=list[PrescriptionRead])
async def list_prescriptions(
    current_user: CurrentUser, session: DbSession, patient_id: uuid.UUID | None = None
) -> list[PrescriptionRead]:
    prescriptions = await PrescriptionService(session).list_my_prescriptions(
        current_user=current_user, patient_id=patient_id
    )
    return [PrescriptionRead.model_validate(prescription) for prescription in prescriptions]


@router.get("/{prescription_id}", response_model=PrescriptionRead)
async def get_prescription(prescription_id: uuid.UUID, current_user: CurrentUser, session: DbSession) -> PrescriptionRead:
    prescription = await PrescriptionService(session).get_my_prescription(
        current_user=current_user, prescription_id=prescription_id
    )
    return PrescriptionRead.model_validate(prescription)


@router.get("/{prescription_id}/pdf")
async def get_prescription_pdf(prescription_id: uuid.UUID, current_user: CurrentUser, session: DbSession) -> Response:
    prescription = await PrescriptionService(session).get_my_prescription(
        current_user=current_user, prescription_id=prescription_id
    )
    doctor_profile = await DoctorProfileRepository(session).get_by_user_id(current_user.id)
    if doctor_profile is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Doctor profile not set up")

    pdf_bytes = generate_prescription_pdf(
        doctor_profile=doctor_profile, patient=prescription.patient, prescription=prescription
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="prescription-{prescription_id}.pdf"'},
    )
