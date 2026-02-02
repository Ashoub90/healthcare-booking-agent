from fastapi import APIRouter
from typing import List
from app.schemas.appointment import Appointment

router = APIRouter()


@router.get("/", response_model=List[Appointment])
async def list_appointments():
    """Return a list of appointments (stub)."""
    return []
