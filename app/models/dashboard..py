from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import User, Patient, Appointment, RoleEnum, AppointmentStatus
from ..auth import login_required

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/individual/dashboard", response_class=HTMLResponse)
def individual_dashboard(
    request: Request,
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    today = date.today()
    context = {"request": request, "user": user}

    if user.role == RoleEnum.DOCTOR:
        context["total_assigned"] = db.query(Appointment).filter(Appointment.doctor_id == user.id).count()
        context["today_queue"] = db.query(Appointment).filter(
            Appointment.doctor_id == user.id,
            Appointment.appointment_date == today,
            Appointment.status != AppointmentStatus.COMPLETED
        ).count()
        context["completed_today"] = db.query(Appointment).filter(
            Appointment.doctor_id == user.id,
            Appointment.appointment_date == today,
            Appointment.status == AppointmentStatus.COMPLETED
        ).count()
        context["my_appointments"] = db.query(Appointment).filter(Appointment.doctor_id == user.id).order_by(Appointment.created_at.desc()).limit(15).all()

    elif user.role == RoleEnum.RECEPTIONIST:
        context["total_created"] = db.query(Appointment).filter(Appointment.created_by_id == user.id).count()
        context["created_today"] = db.query(Appointment).filter(
            Appointment.created_by_id == user.id,
            Appointment.appointment_date == today
        ).count()
        context["my_entries"] = db.query(Appointment).filter(Appointment.created_by_id == user.id).order_by(Appointment.created_at.desc()).limit(15).all()

    return templates.TemplateResponse("individual_dashboard.html", context)

@router.get("/admin/live", response_class=HTMLResponse)
def admin_live_dashboard(
    request: Request,
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin role required for HMI Access")

    today = date.today()
    doctors = db.query(User).filter(User.role == RoleEnum.DOCTOR).all()
    doctor_queues = []

    for doc in doctors:
        waiting = db.query(Appointment).filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date == today,
            Appointment.status == AppointmentStatus.WAITING
        ).count()
        in_consultation = db.query(Appointment).filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date == today,
            Appointment.status == AppointmentStatus.IN_CONSULTATION
        ).count()
        completed = db.query(Appointment).filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date == today,
            Appointment.status == AppointmentStatus.COMPLETED
        ).count()

        doctor_queues.append({
            "doctor": doc,
            "waiting": waiting,
            "in_consultation": in_consultation,
            "completed": completed,
            "total_today": waiting + in_consultation + completed
        })

    total_patients_today = db.query(Appointment).filter(Appointment.appointment_date == today).count()

    return templates.TemplateResponse("admin_live.html", {
        "request": request,
        "user": user,
        "doctor_queues": doctor_queues,
        "total_patients_today": total_patients_today
    })

@router.get("/admin/history", response_class=HTMLResponse)
def admin_history_dashboard(
    request: Request,
    period: str = "daily",  # daily, monthly, quarterly
    user: User = Depends(login_required),
    db: Session = Depends(get_db)
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin role required for HMI Access")

    today = date.today()
    if period == "daily":
        start_date = today
    elif period == "monthly":
        start_date = today - timedelta(days=30)
    elif period == "quarterly":
        start_date = today - timedelta(days=90)
    else:
        start_date = today

    # Doctor patient counts
    doctor_stats = db.query(
        User.full_name,
        func.count(Appointment.id).label("total_treated")
    ).join(Appointment, Appointment.doctor_id == User.id)\
     .filter(Appointment.appointment_date >= start_date, Appointment.status == AppointmentStatus.COMPLETED)\
     .group_by(User.full_name).all()

    # Breakdown by Receptionist entries
    receptionist_stats = db.query(
        User.full_name,
        func.count(Appointment.id).label("total_booked")
    ).join(Appointment, Appointment.created_by_id == User.id)\
     .filter(Appointment.appointment_date >= start_date)\
     .group_by(User.full_name).all()

    # Breakdown by Illness / Category
    illness_stats = db.query(
        Patient.primary_illness,
        func.count(Patient.id).label("illness_count")
    ).group_by(Patient.primary_illness).all()

    return templates.TemplateResponse("admin_history.html", {
        "request": request,
        "user": user,
        "period": period,
        "doctor_stats": doctor_stats,
        "receptionist_stats": receptionist_stats,
        "illness_stats": illness_stats
    })