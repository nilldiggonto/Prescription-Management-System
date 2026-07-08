import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DoctorProfileTemplate(str, Enum):
    CLASSIC = "classic"
    MODERN = "modern"
    MINIMAL = "minimal"


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    degrees: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str | None] = mapped_column(String(150), nullable=True)
    registration_number: Mapped[str] = mapped_column(String(100), nullable=False)
    hospital_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    chamber_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    signature_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    watermark_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    template: Mapped[DoctorProfileTemplate] = mapped_column(
        String(20),
        default=DoctorProfileTemplate.CLASSIC,
        server_default=DoctorProfileTemplate.CLASSIC.value,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
