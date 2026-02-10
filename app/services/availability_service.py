from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db import models

LEAD_TIME_HOURS = 1


def check_availability(
    appointment_date: date,
    service_type_id: int,
    db: Session
):
    service = db.query(models.ServiceType).filter(
        models.ServiceType.id == service_type_id,
        models.ServiceType.active == True
    ).first()

    if not service:
        raise ValueError("Service type not found or inactive")

    duration = timedelta(minutes=service.duration_minutes)
    
    if isinstance(appointment_date, str):
        try:
            # Matches format 'YYYY-MM-DD'
            appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {appointment_date}. Expected YYYY-MM-DD.")
        
    day_name = appointment_date.strftime("%A")
    business_hour = db.query(models.BusinessHour).filter(
        models.BusinessHour.day_of_week == day_name
    ).first()

    if not business_hour or business_hour.is_closed:
        return []

    start_dt = datetime.combine(appointment_date, business_hour.open_time)
    end_dt = datetime.combine(appointment_date, business_hour.close_time)

    # Existing appointments
    appointments = db.query(models.Appointment).filter(
        models.Appointment.appointment_date == appointment_date,
        models.Appointment.status != "cancelled"
    ).all()

    booked_slots = [
        (
            datetime.combine(appointment_date, a.start_time),
            datetime.combine(appointment_date, a.end_time)
        )
        for a in appointments
    ]

    # Blocked slots (lunch, holidays, etc.)
    blocked = db.query(models.BlockedSlot).filter(
        models.BlockedSlot.date == appointment_date
    ).all()

    blocked_slots = [
        (
            datetime.combine(appointment_date, b.start_time),
            datetime.combine(appointment_date, b.end_time)
        )
        for b in blocked
    ]

    all_blocked = booked_slots + blocked_slots

    now = datetime.now(timezone.utc)
    min_allowed = now + timedelta(hours=LEAD_TIME_HOURS)

    available_slots = []
    current = start_dt

    while current + duration <= end_dt:
        slot_end = current + duration

        # Lead time check
        if appointment_date == now.date() and current < min_allowed:
            current += timedelta(minutes=15)
            continue

        conflict = any(
            current < blocked_end and slot_end > blocked_start
            for blocked_start, blocked_end in all_blocked
        )

        if not conflict:
            available_slots.append({
                "start_time": current.time(),
                "end_time": slot_end.time()
            })

        current += timedelta(minutes=15)

    return available_slots
