from sqlalchemy.orm import Session
from typing import Optional
from app.db import models
from app.services.logging_service import log_agent_action_service



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
    
    log_agent_action_service(
        db=db,
        patient_id=patient.id,
        log_context="[System Auto-Log]",
        agent_action="PATIENT_REGISTERED",
        system_decision=f"New patient {full_name} added to database.",
        confidence_score=1.0
    )
    
    return patient
