from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.patient import PatientCreate, PatientOut
from app.services import patient_service

router = APIRouter()


@router.post("/", response_model=PatientOut)
def create_patient_api(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    try:
        return patient_service.create_patient(
            db=db,
            full_name=patient.full_name,
            phone_number=patient.phone_number,
            email=patient.email,
            is_insured=patient.is_insured,
            insurance_provider=patient.insurance_provider,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PatientOut])
def list_patients(db: Session = Depends(get_db)):
    return db.query(patient_service.models.Patient).all()


@router.get("/lookup/{phone_number}", response_model=PatientOut)
def get_patient_by_phone_api(
    phone_number: str,
    db: Session = Depends(get_db)
):
    patient = patient_service.get_patient_by_phone(db, phone_number)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
