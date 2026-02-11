from datetime import datetime, timedelta, date, time, timezone
from sqlalchemy.orm import Session
from app.db import models
from app.services.calendar_service import CalendarService

LEAD_TIME_HOURS = 1
google_cal = CalendarService()


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

    try:
            google_busy = google_cal.get_busy_slots(appointment_date)
            # Check if the requested start/end overlaps with any Google event
            for g_start, g_end in google_busy:
                if start_dt < g_end and end_dt > g_start:
                    raise ValueError("This slot is blocked on the doctor's external Google Calendar.")
    except Exception as e:
            # If Google is down, we still allow the booking based on Postgres rules
            print(f"Warning: Could not verify Google Calendar availability: {e}")

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

    try:
        full_start = datetime.combine(appointment_date, start_time)
        full_end = full_start + timedelta(minutes=service.duration_minutes)
        
        # Capture the response from Google
        event = google_cal.create_event(
            summary=f"Appointment: {patient.full_name} ({service.name})",
            start_time=full_start, # If your create_event method handles objects, keep this. 
            end_time=full_end      # But usually it needs full_start.isoformat()
        )
        
        # Save the Google Event ID to your Postgres record
        appointment.google_event_id = event.get('id')
        db.commit() 
        
    except Exception as e:
        print(f"Postgres succeeded but Google sync failed: {e}")

    return appointment

def get_appointments_by_patient(db: Session, patient_id: int):
    """
    Retrieves all non-cancelled appointments for a specific patient,
    ordered by date and time (soonest first).
    """
    return db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient_id,
        models.Appointment.status != "cancelled"
    ).order_by(
        models.Appointment.appointment_date.asc(), 
        models.Appointment.start_time.asc()
    ).all()

def cancel_appointment_service(db: Session, appointment_id: int):
    """
    Updates status to 'cancelled' and removes from Google Calendar.
    """
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise ValueError(f"Appointment with ID {appointment_id} not found.")

    # NEW: Remove from Google Calendar if an ID exists
    if hasattr(appointment, 'google_event_id') and appointment.google_event_id:
        try:
            google_cal.delete_event(appointment.google_event_id)
        except Exception as e:
            print(f"Warning: Could not delete Google event {appointment.google_event_id}: {e}")
    
    appointment.status = "cancelled"
    db.commit()
    db.refresh(appointment)
    return appointment