from datetime import datetime, timedelta, date, time, timezone
from sqlalchemy.orm import Session
from app.db import models

LEAD_TIME_HOURS = 1

def parse_time_string(time_str):
    # List the common formats the agent might send
    formats = ["%I:%M %p", "%H:%M:%S", "%H:%M"]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
            
    raise ValueError(f"Time data '{time_str}' does not match any expected formats.")

def create_appointment_service(
    db: Session,
    patient_id: int,
    service_type_id: int,
    appointment_date: date,
    start_time: time,
):
    # 1. Convert appointment_date string to date object
    if isinstance(appointment_date, str):
        appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()

    # 2. Convert start_time string (e.g., "12:00 PM") to time object
    if isinstance(start_time, str):
        start_time = parse_time_string(start_time)
    
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
    now_naive_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    
    if start_dt < now_naive_utc + timedelta(hours=LEAD_TIME_HOURS):
        raise ValueError(
            f"Appointments must be booked at least {LEAD_TIME_HOURS} hour(s) in advance. "
            f"Current UTC time: {now_naive_utc.strftime('%H:%M')}, "
            f"Requested: {start_dt.strftime('%H:%M')}"
        )

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
