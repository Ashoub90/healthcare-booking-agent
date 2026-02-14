from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentOut
from app.services import appointment_service

router = APIRouter()


@router.post("/", response_model=AppointmentOut)
def create_appointment_api(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
):
    try:
        return appointment_service.create_appointment(
            db=db,
            patient_id=appointment.patient_id,
            service_type_id=appointment.service_type_id,
            appointment_date=appointment.appointment_date,
            start_time=appointment.start_time,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[AppointmentOut])
def list_appointments(db: Session = Depends(get_db)):
    return appointment_service.get_appointments(db)


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_status_api(
    appointment_id: int, 
    new_status: str, 
    background_tasks: BackgroundTasks, # Added this line
    db: Session = Depends(get_db)
):
    try:
        return appointment_service.update_appointment_status_service(
            db=db, 
            appointment_id=appointment_id, 
            new_status=new_status,
            background_tasks=background_tasks # Pass it to the service
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))