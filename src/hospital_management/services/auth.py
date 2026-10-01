from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from hospital_management.database.models.staff import StaffProfile
from hospital_management.database.repositories import staff as staff_repository
from hospital_management.helpers.security import hash_password, verify_password
from hospital_management.schemas.staff import StaffProfileCreate


class DuplicateProfileError(Exception):
	pass


def register_profile(database: Session, profile: StaffProfileCreate) -> StaffProfile:
	if staff_repository.get_by_email(database, str(profile.email)):
		raise DuplicateProfileError("A profile already exists for this email address")

	try:
		return staff_repository.create(database, profile, hash_password(profile.password))
	except IntegrityError as error:
		database.rollback()
		raise DuplicateProfileError("Email or license number is already registered") from error


def authenticate(database: Session, email: str, password: str) -> StaffProfile | None:
	profile = staff_repository.get_by_email(database, email)
	if profile is None or not verify_password(password, profile.password_hash):
		return None
	return profile
