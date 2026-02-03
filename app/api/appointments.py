from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.db.session import get_db
from app.db import models
from app.schemas.appointment import AppointmentCreate, AppointmentOut

router = APIRouter()


@router.post("/", response_model=AppointmentOut)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):

    patient = db.query(models.Patient).filter(
        models.Patient.id == appointment.patient_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    service = db.query(models.ServiceType).filter(
        models.ServiceType.id == appointment.service_type_id
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service type not found")

    start_dt = datetime.combine(appointment.appointment_date, appointment.start_time)
    end_time = (start_dt + timedelta(minutes=service.duration_minutes)).time()

    conflict = db.query(models.Appointment).filter(
        models.Appointment.appointment_date == appointment.appointment_date,
        models.Appointment.start_time < end_time,
        models.Appointment.end_time > appointment.start_time
    ).first()

    if conflict:
        raise HTTPException(status_code=400, detail="Time slot already booked")

    db_appointment = models.Appointment(
        patient_id=appointment.patient_id,
        service_type_id=appointment.service_type_id,
        appointment_date=appointment.appointment_date,
        start_time=appointment.start_time,
        end_time=end_time
    )

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


@router.get("/", response_model=List[AppointmentOut])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()
