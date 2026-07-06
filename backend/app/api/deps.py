from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.email_service import EmailSender, get_email_sender

DbSession = Annotated[AsyncSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]
EmailSenderDep = Annotated[EmailSender, Depends(get_email_sender)]


def get_auth_service(
    session: DbSession,
    settings: AppSettings,
    email_sender: EmailSenderDep,
) -> AuthService:
    return AuthService(session=session, settings=settings, email_sender=email_sender)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
