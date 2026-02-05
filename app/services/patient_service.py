from sqlalchemy.orm import Session
from typing import Optional
from app.db import models


def get_patient_by_phone(db: Session, phone_number: str) -> Optional[models.Patient]:
    return (
        db.query(models.Patient)
        .filter(models.Patient.phone_number == phone_number)
        .first()
    )


def get_patient_by_id(db: Session, patient_id: int) -> Optional[models.Patient]:
    return (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )


def create_patient(
    db: Session,
    full_name: str,
    phone_number: str,
    email: Optional[str],
    is_insured: bool,
    insurance_provider: Optional[str],
) -> models.Patient:

    existing = get_patient_by_phone(db, phone_number)
    if existing:
        raise ValueError("Patient already exists")

    patient = models.Patient(
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        is_insured=is_insured,
        insurance_provider=insurance_provider,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
