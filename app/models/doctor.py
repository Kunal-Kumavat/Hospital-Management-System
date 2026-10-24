import os
import shutil
from datetime import date
from fastapi import APIRouter, Depends, Form, Request, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models import User, Patient, Appointment, ConsultationRecord, MedicalReport, RoleEnum, AppointmentStatus
from ..auth import login_required

router = APIRouter(prefix="/doctor")
templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = "static/uploads"

def ensure_doctor(user: User):
    if user.role != RoleEnum.DOCTOR and not user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

@router.get("/consultation", response_class=HTMLResponse)
def doctor_consultation(
    request: Request,
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    ensure_doctor(user)
    today = date.today()
    # Show active queue for this specific doctor
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == user.id,
        Appointment.appointment_date == today,
        Appointment.status != AppointmentStatus.COMPLETED
    ).order_by(Appointment.token_number.asc()).all()

    return templates.TemplateResponse("doctor_consultation.html", {
        "request": request,
        "appointments": appointments,
        "user": user
    })

@router.get("/patient/{patient_id}/history", response_class=HTMLResponse)
def view_patient_history(
    patient_id: int,
    request: Request,
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Fetch all records, prescriptions, and reports
    appointments = db.query(Appointment).filter(Appointment.patient_id == patient_id).order_by(Appointment.created_at.desc()).all()
    reports = db.query(MedicalReport).filter(MedicalReport.patient_id == patient_id).order_by(MedicalReport.uploaded_at.desc()).all()

    return templates.TemplateResponse("doctor_history.html", {
        "request": request,
        "patient": patient,
        "appointments": appointments,
        "reports": reports,
        "user": user
    })

@router.post("/appointment/{appointment_id}/prescribe")
async def add_prescription_and_reports(
    appointment_id: int,
    request: Request,
    diagnosis: str = Form(...),
    prescription: str = Form(...),
    notes: str = Form(""),
    report_title: str = Form(None),
    report_type: str = Form(None),
    report_file: UploadFile = File(None),
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    ensure_doctor(user)
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Add consultation record
    consultation = ConsultationRecord(
        appointment_id=appointment.id,
        diagnosis=diagnosis,
        prescription=prescription,
        notes=notes
    )
    db.add(consultation)
    appointment.status = AppointmentStatus.COMPLETED

    # Save and link report image (ECG, X-Ray, etc.) if provided
    if report_file and report_file.filename:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"{int(date.today().strftime('%Y%m%d'))}_{appointment.patient_id}_{report_file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(report_file.file, buffer)

        med_report = MedicalReport(
            patient_id=appointment.patient_id,
            title=report_title or "Report",
            report_type=report_type or "General",
            file_path=f"/static/uploads/{filename}"
        )
        db.add(med_report)

    db.commit()
    return RedirectResponse(url="/doctor/consultation", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/search", response_class=HTMLResponse)
def search_patients(
    request: Request,
    q: str = "",
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    patients = []
    if q:
        patients = db.query(Patient).filter(
            or_(Patient.name.ilike(f"%{q}%"), Patient.contact.ilike(f"%{q}%"))
        ).all()
    return templates.TemplateResponse("doctor_history.html", {
        "request": request,
        "patients_search": patients,
        "query": q,
        "user": user
    })