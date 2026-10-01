from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from hospital_management.database.models.staff import StaffRole


class StaffProfileCreate(BaseModel):
	role: StaffRole
	full_name: str = Field(min_length=2, max_length=120)
	email: EmailStr
	phone: str = Field(min_length=7, max_length=30)
	profession: str = Field(min_length=2, max_length=120)
	area_of_expertise: str = Field(min_length=2, max_length=160)
	qualification: str = Field(min_length=2, max_length=160)
	license_number: str | None = Field(default=None, max_length=80)
	years_of_experience: int = Field(ge=0, le=80)
	password: str = Field(min_length=8, max_length=128)

	@model_validator(mode="after")
	def validate_doctor_license(self) -> "StaffProfileCreate":
		if self.role == StaffRole.DOCTOR and not self.license_number:
			raise ValueError("A medical license number is required for doctors")
		if self.role == StaffRole.RECEPTIONIST:
			self.license_number = None
		return self


class StaffProfileResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	role: StaffRole
	full_name: str
	email: EmailStr
	phone: str
	profession: str
	area_of_expertise: str
	qualification: str
	license_number: str | None
	years_of_experience: int
	created_at: datetime
