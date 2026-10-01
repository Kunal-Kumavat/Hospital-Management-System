from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hospital_management.database.session import get_db
from hospital_management.schemas.patient import PatientCreate, PatientResponse
from hospital_management.services.patient import create_patient

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient_entry(
	patient: PatientCreate, database: Session = Depends(get_db)
) -> PatientResponse:
	return create_patient(database, patient)
