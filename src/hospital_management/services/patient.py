from sqlalchemy.orm import Session

from hospital_management.database.models.patient import Patient
from hospital_management.database.repositories import patient as patient_repository
from hospital_management.schemas.patient import PatientCreate


def create_patient(database: Session, patient: PatientCreate) -> Patient:
	return patient_repository.create(database, patient)
