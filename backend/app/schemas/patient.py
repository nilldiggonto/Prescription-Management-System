import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.patient import PatientGender


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    age: int | None
    gender: PatientGender
    phone: str | None
    address: str | None
    created_at: datetime


class PatientWrite(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    age: int | None = Field(default=None, ge=0, le=150)
    gender: PatientGender
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)
