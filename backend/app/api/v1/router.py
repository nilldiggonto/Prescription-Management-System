from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.billing import router as billing_router
from app.api.v1.doctor_profile import router as doctor_profile_router
from app.api.v1.patients import router as patients_router
from app.api.v1.prescriptions import router as prescriptions_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(doctor_profile_router)
api_router.include_router(patients_router)
api_router.include_router(prescriptions_router)
api_router.include_router(billing_router)
api_router.include_router(admin_router)
