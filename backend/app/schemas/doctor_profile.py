import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DoctorProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    degrees: str
    specialization: str | None
    registration_number: str
    hospital_name: str | None
    chamber_address: str | None
    phone: str | None
    signature_url: str | None
    logo_url: str | None
    created_at: datetime
    updated_at: datetime


class DoctorProfileWrite(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    degrees: str = Field(min_length=1, max_length=255)
    specialization: str | None = Field(default=None, max_length=150)
    registration_number: str = Field(min_length=1, max_length=100)
    hospital_name: str | None = Field(default=None, max_length=200)
    chamber_address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=30)
    signature_url: str | None = Field(default=None, max_length=500)
    logo_url: str | None = Field(default=None, max_length=500)
