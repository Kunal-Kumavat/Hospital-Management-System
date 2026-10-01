from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PatientCreate(BaseModel):
	full_name: str = Field(min_length=2, max_length=120)
	age: int = Field(ge=0, le=130)
	contact_number: str = Field(min_length=7, max_length=30)
	address: str = Field(min_length=5, max_length=500)
	appointment_reason: str | None = Field(default=None, max_length=500)


class PatientResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	full_name: str
	age: int
	contact_number: str
	address: str
	appointment_reason: str | None
	created_at: datetime
