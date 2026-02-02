from fastapi import APIRouter
from typing import List
from app.schemas.patient import Patient

router = APIRouter()


@router.get("/", response_model=List[Patient])
async def list_patients():
    """Return a list of patients (stub)."""
    return []
