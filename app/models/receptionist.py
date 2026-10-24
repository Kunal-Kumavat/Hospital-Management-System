from datetime import date, datetime
from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models import User, Patient, Appointment, RoleEnum, AppointmentStatus
from ..auth import login_required

router = APIRouter(prefix="/receptionist")
templates = Jinja2Templates(directory="app/templates")

def ensure_receptionist(user: User):
    if user.role != RoleEnum.RECEPTIONIST and not user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

@router.get("/patients", response_class=HTMLResponse)
def list_or_search_patients(
    request: Request,
    q: str = "",
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    ensure_receptionist(user)
    doctors = db.query(User).filter(User.role == RoleEnum.DOCTOR).all()
    query = db.query(Patient)
    if q:
        query = query.filter(or_(Patient.name.ilike(f"%{q}%"), Patient.contact.ilike(f"%{q}%")))
    patients = query.order_by(Patient.id.desc()).all()
    return templates.TemplateResponse("receptionist_patients.html", {
        "request": request,
        "patients": patients,
        "doctors": doctors,
        "query": q,
        "user": user
    })

@router.post("/patients/create")
def create_patient(
    request: Request,
    name: str = Form(...),
    dob: str = Form(...),
    contact: str = Form(...),
    address: str = Form(""),
    blood_group: str = Form(""),
    height_cm: float = Form(...),
    weight_kg: float = Form(...),
    primary_illness: str = Form(...),
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    ensure_receptionist(user)
    # BMI formula: weight (kg) / [height (m)]^2
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 2) if height_m > 0 else 0.0

    patient = Patient(
        name=name,
        dob=datetime.strptime(dob, "%Y-%m-%d").date(),
        contact=contact,
        address=address,
        blood_group=blood_group,
        height_cm=height_cm,
        weight_kg=weight_kg,
        bmi=bmi,
        primary_illness=primary_illness
    )
    db.add(patient)
    db.commit()
    return RedirectResponse(url="/receptionist/patients", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/queue/add")
def add_to_queue(
    request: Request,
    patient_id: int = Form(...),
    doctor_id: int = Form(...),
    illness_complaint: str = Form(...),
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    ensure_receptionist(user)
    today = date.today()
    # Generate sequential token for this specific doctor today
    last_token = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == today
    ).count()

    token_number = last_token + 1
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        created_by_id=user.id,
        token_number=token_number,
        appointment_date=today,
        illness_complaint=illness_complaint,
        status=AppointmentStatus.WAITING
    )
    db.add(appointment)
    db.commit()
    return RedirectResponse(url="/receptionist/queue", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/queue", response_class=HTMLResponse)
def view_today_queue(
    request: Request,
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    ensure_receptionist(user)
    today = date.today()
    appointments = db.query(Appointment).filter(Appointment.appointment_date == today).order_by(Appointment.token_number.asc()).all()
    return templates.TemplateResponse("receptionist_queue.html", {
        "request": request,
        "appointments": appointments,
        "user": user
    })