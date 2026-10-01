from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from hospital_management.database.session import get_db
from hospital_management.helpers.security import create_access_token
from hospital_management.schemas.auth import LoginRequest, LoginResponse
from hospital_management.services.auth import authenticate

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, database: Session = Depends(get_db)) -> LoginResponse:
	profile = authenticate(database, str(credentials.email), credentials.password)
	if profile is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid email or password",
		)

	return LoginResponse(
		access_token=create_access_token(profile.id, profile.role),
		profile=profile,
	)
