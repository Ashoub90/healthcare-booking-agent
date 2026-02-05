from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Dict, Any

from app.db.session import get_db
from app.services.availability_service import check_availability

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
def get_availability(
    appointment_date: date,
    service_type_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns available time slots for a given date and service type.
    """

    try:
        slots = check_availability(
            appointment_date=appointment_date,
            service_type_id=service_type_id,
            db=db
        )
        return slots

    except ValueError as e:
        # Business-rule error (e.g. service inactive)
        raise HTTPException(status_code=400, detail=str(e))
