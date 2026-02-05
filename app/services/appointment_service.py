from datetime import datetime, timedelta, date, time, timezone
from sqlalchemy.orm import Session
from app.db import models

LEAD_TIME_HOURS = 1


def create_appointment(
    db: Session,
    patient_id: int,
    service_type_id: int,
    appointment_date: date,
    start_time: time,
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id
    ).first()
    if not patient:
        raise ValueError("Patient not found")

    service = db.query(models.ServiceType).filter(
        models.ServiceType.id == service_type_id,
        models.ServiceType.active == True
    ).first()
    if not service:
        raise ValueError("Service type not found or inactive")

    start_dt = datetime.combine(appointment_date, start_time)
    end_dt = start_dt + timedelta(minutes=service.duration_minutes)

    # Lead time enforcement
    if start_dt < datetime.now(timezone.utc) + timedelta(hours=LEAD_TIME_HOURS):
        raise ValueError("Appointments must be booked at least 1 hour in advance")

    # Conflict with existing appointments
    conflict = db.query(models.Appointment).filter(
        models.Appointment.appointment_date == appointment_date,
        models.Appointment.start_time < end_dt.time(),
        models.Appointment.end_time > start_time,
        models.Appointment.status != "cancelled"
    ).first()

    if conflict:
        raise ValueError("Time slot already booked")

    # Conflict with blocked slots
    blocked = db.query(models.BlockedSlot).filter(
        models.BlockedSlot.date == appointment_date,
        models.BlockedSlot.start_time < end_dt.time(),
        models.BlockedSlot.end_time > start_time
    ).first()

    if blocked:
        raise ValueError("Time slot is blocked")

    appointment = models.Appointment(
        patient_id=patient_id,
        service_type_id=service_type_id,
        appointment_date=appointment_date,
        start_time=start_time,
        end_time=end_dt.time(),
        status="pending"
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
