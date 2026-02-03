from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.db.session import get_db
from app.db import models

router = APIRouter()


@router.get("/")
def get_availability(date: date, service_type_id: int, db: Session = Depends(get_db)):

    business_hours = db.query(models.BusinessHour).all()
    appointments = db.query(models.Appointment).filter(
        models.Appointment.appointment_date == date
    ).all()

    return {
        "date": date,
        "business_hours": business_hours,
        "appointments": appointments
    }
