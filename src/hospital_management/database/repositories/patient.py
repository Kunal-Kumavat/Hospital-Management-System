from sqlalchemy.orm import Session

from hospital_management.database.models.patient import Patient
from hospital_management.schemas.patient import PatientCreate


def create(database: Session, patient: PatientCreate) -> Patient:
	patient_record = Patient(**patient.model_dump())
	database.add(patient_record)
	database.commit()
	database.refresh(patient_record)
	return patient_record
