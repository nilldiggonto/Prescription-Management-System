import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.patient import PatientRead, PatientWrite


class MedicineItem(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    dosage: str = Field(min_length=1, max_length=100)
    frequency: str = Field(min_length=1, max_length=100)
    duration: str = Field(min_length=1, max_length=100)
    instructions: str | None = Field(default=None, max_length=300)


class MedicineRead(MedicineItem):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class PrescriptionCreate(BaseModel):
    patient_id: uuid.UUID | None = None
    new_patient: PatientWrite | None = None
    diagnosis: str | None = Field(default=None, max_length=5000)
    advice: str | None = Field(default=None, max_length=5000)
    follow_up_date: date | None = None
    medicines: list[MedicineItem] = Field(min_length=1)

    @model_validator(mode="after")
    def _exactly_one_patient_source(self) -> "PrescriptionCreate":
        if (self.patient_id is None) == (self.new_patient is None):
            raise ValueError("Provide exactly one of patient_id or new_patient")
        return self


class PrescriptionRead(BaseModel):
    id: uuid.UUID
    patient: PatientRead
    diagnosis: str | None
    advice: str | None
    follow_up_date: date | None
    medicines: list[MedicineRead]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
