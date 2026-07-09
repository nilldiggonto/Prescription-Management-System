import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import AppSettings, CurrentAdmin, DbSession, verify_csrf_token
from app.repositories.user_repository import UserRepository
from app.schemas.admin import AdminStatusUpdate, AdminSubscriptionUpdate, AdminUserRead
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserRead])
async def list_users(current_admin: CurrentAdmin, session: DbSession, settings: AppSettings) -> list[AdminUserRead]:
    return await SubscriptionService(session, settings).list_all_with_usage()


@router.patch(
    "/users/{user_id}/subscription", response_model=AdminUserRead, dependencies=[Depends(verify_csrf_token)]
)
async def override_subscription(
    user_id: uuid.UUID,
    payload: AdminSubscriptionUpdate,
    current_admin: CurrentAdmin,
    session: DbSession,
    settings: AppSettings,
) -> AdminUserRead:
    return await SubscriptionService(session, settings).override_plan(user_id, payload.plan)


@router.patch("/users/{user_id}/status", response_model=AdminUserRead, dependencies=[Depends(verify_csrf_token)])
async def set_user_status(
    user_id: uuid.UUID,
    payload: AdminStatusUpdate,
    current_admin: CurrentAdmin,
    session: DbSession,
    settings: AppSettings,
) -> AdminUserRead:
    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = payload.is_active
    await session.commit()

    return await SubscriptionService(session, settings).get_admin_user_read(user_id)
