from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db import models
from app.schemas.service_type import ServiceTypeCreate, ServiceTypeOut

router = APIRouter()


@router.get("/", response_model=List[ServiceTypeOut])
def list_service_types(db: Session = Depends(get_db)):
    return db.query(models.ServiceType).filter(models.ServiceType.active == True).all()


@router.post("/", response_model=ServiceTypeOut)
def create_service_type(service: ServiceTypeCreate, db: Session = Depends(get_db)):
    db_service = models.ServiceType(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service
