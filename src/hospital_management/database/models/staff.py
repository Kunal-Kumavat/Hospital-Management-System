from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from hospital_management.database.base import Base


class StaffRole(str, Enum):
	RECEPTIONIST = "receptionist"
	DOCTOR = "doctor"


class StaffProfile(Base):
	__tablename__ = "staff_profiles"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	role: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
	full_name: Mapped[str] = mapped_column(String(120), nullable=False)
	email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
	phone: Mapped[str] = mapped_column(String(30), nullable=False)
	profession: Mapped[str] = mapped_column(String(120), nullable=False)
	area_of_expertise: Mapped[str] = mapped_column(String(160), nullable=False)
	qualification: Mapped[str] = mapped_column(String(160), nullable=False)
	license_number: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
	years_of_experience: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
	)
