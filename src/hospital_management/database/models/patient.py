from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hospital_management.database.base import Base


class Patient(Base):
	__tablename__ = "patients"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	full_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
	age: Mapped[int] = mapped_column(Integer, nullable=False)
	contact_number: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
	address: Mapped[str] = mapped_column(Text, nullable=False)
	appointment_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
	)
