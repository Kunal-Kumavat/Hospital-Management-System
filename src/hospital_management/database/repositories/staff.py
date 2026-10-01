from sqlalchemy import select
from sqlalchemy.orm import Session

from hospital_management.database.models.staff import StaffProfile
from hospital_management.schemas.staff import StaffProfileCreate


def get_by_email(database: Session, email: str) -> StaffProfile | None:
    return database.scalar(select(StaffProfile).where(StaffProfile.email == email.lower()))


def create(
    database: Session, profile: StaffProfileCreate, password_hash: str
) -> StaffProfile:
    staff_profile = StaffProfile(
        **profile.model_dump(exclude={"password", "email", "role"}),
        email=str(profile.email).lower(),
        role=profile.role.value,
        password_hash=password_hash,
    )
    database.add(staff_profile)
    database.commit()
    database.refresh(staff_profile)
    return staff_profile