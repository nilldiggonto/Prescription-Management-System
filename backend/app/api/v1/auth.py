from fastapi import APIRouter, BackgroundTasks, status

from app.api.deps import AuthServiceDep
from app.schemas.auth import RegisterRequest, VerifyEmailRequest, VerifyEmailResponse
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest, background_tasks: BackgroundTasks, auth_service: AuthServiceDep
) -> UserRead:
    user = await auth_service.register(
        email=payload.email, password=payload.password, background_tasks=background_tasks
    )
    return UserRead.model_validate(user)


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(payload: VerifyEmailRequest, auth_service: AuthServiceDep) -> VerifyEmailResponse:
    await auth_service.verify_email(email=payload.email, otp=payload.otp)
    return VerifyEmailResponse(message="Email verified successfully")
