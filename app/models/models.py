import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class RoleEnum(str, enum.Enum):
    DOCTOR = "Doctor"
    RECEPTIONIST = "Receptionist"

class AppointmentStatus(str, enum.Enum):
    WAITING = "Waiting"
    IN_CONSULTATION = "In Consultation"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    dob = Column(Date, nullable=False)
    designation = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    specialization = Column(String(100), nullable=True)  # For doctors (e.g. Cardiology, General)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    appointments = relationship("Appointment", back_populates="doctor", foreign_keys="Appointment.doctor_id")
    created_appointments = relationship("Appointment", back_populates="created_by", foreign_keys="Appointment.created_by_id")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    dob = Column(Date, nullable=False)
    contact = Column(String(20), index=True, nullable=False)
    address = Column(String(255), nullable=True)
    blood_group = Column(String(10), nullable=True)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    primary_illness = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    reports = relationship("MedicalReport", back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_number = Column(Integer, nullable=False)
    appointment_date = Column(Date, default=date.today)
    illness_complaint = Column(Text, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.WAITING)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", back_populates="appointments", foreign_keys=[doctor_id])
    created_by = relationship("User", back_populates="created_appointments", foreign_keys=[created_by_id])
    consultation = relationship("ConsultationRecord", back_populates="appointment", uselist=False)

class ConsultationRecord(Base):
    __tablename__ = "consultation_records"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True)
    diagnosis = Column(Text, nullable=False)
    prescription = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="consultation")

class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    title = Column(String(100), nullable=False)
    report_type = Column(String(50), nullable=False)  # X-Ray, ECG, Blood Test, etc.
    file_path = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="reports")