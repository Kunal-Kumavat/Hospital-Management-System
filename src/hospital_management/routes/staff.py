from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from hospital_management.database.session import get_db
from hospital_management.schemas.staff import StaffProfileCreate, StaffProfileResponse
from hospital_management.services.auth import DuplicateProfileError, register_profile

router = APIRouter(prefix="/api/profiles", tags=["staff profiles"])


@router.post("", response_model=StaffProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
	profile: StaffProfileCreate, database: Session = Depends(get_db)
) -> StaffProfileResponse:
	try:
		return register_profile(database, profile)
	except DuplicateProfileError as error:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
