from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.doctor_profile import router as doctor_profile_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(doctor_profile_router)
