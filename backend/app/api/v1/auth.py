from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status

from app.api.deps import AppSettings, AuthServiceDep, CurrentUser, verify_csrf_token
from app.core.cookies import ACCESS_TOKEN_COOKIE, clear_auth_cookies, set_auth_cookies
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
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


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(payload: VerifyEmailRequest, auth_service: AuthServiceDep) -> MessageResponse:
    await auth_service.verify_email(email=payload.email, otp=payload.otp)
    return MessageResponse(message="Email verified successfully")


@router.post("/login", response_model=UserRead)
async def login(
    payload: LoginRequest, response: Response, auth_service: AuthServiceDep, settings: AppSettings
) -> UserRead:
    user, raw_access_token, csrf_token = await auth_service.login(
        email=payload.email, password=payload.password, remember_me=payload.remember_me
    )
    set_auth_cookies(
        response,
        access_token_raw=raw_access_token,
        csrf_token=csrf_token,
        remember_me=payload.remember_me,
        settings=settings,
    )
    return UserRead.model_validate(user)


@router.post("/logout", response_model=MessageResponse, dependencies=[Depends(verify_csrf_token)])
async def logout(
    request: Request, response: Response, auth_service: AuthServiceDep, settings: AppSettings
) -> MessageResponse:
    raw_access_token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if raw_access_token is not None:
        await auth_service.logout(raw_access_token=raw_access_token)
    clear_auth_cookies(response, settings)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: ForgotPasswordRequest, background_tasks: BackgroundTasks, auth_service: AuthServiceDep
) -> MessageResponse:
    await auth_service.forgot_password(email=payload.email, background_tasks=background_tasks)
    return MessageResponse(message="If that email exists, a reset code has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordRequest, auth_service: AuthServiceDep) -> MessageResponse:
    await auth_service.reset_password(email=payload.email, otp=payload.otp, new_password=payload.new_password)
    return MessageResponse(message="Password reset successfully")
