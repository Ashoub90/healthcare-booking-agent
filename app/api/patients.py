from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db import models
from app.schemas.patient import PatientCreate, PatientOut

router = APIRouter()


@router.post("/", response_model=PatientOut)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):

    existing = db.query(models.Patient).filter(
        models.Patient.phone_number == patient.phone_number
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Patient already exists")

    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/", response_model=List[PatientOut])
def list_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()


@router.get("/lookup/{phone_number}", response_model=PatientOut)
def get_patient_by_phone(phone_number: str, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(
        models.Patient.phone_number == phone_number
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient
