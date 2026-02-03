from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db import models
from app.schemas.business_hours import BusinessHourCreate, BusinessHourOut

router = APIRouter()


@router.get("/", response_model=List[BusinessHourOut])
def list_business_hours(db: Session = Depends(get_db)):
    return db.query(models.BusinessHour).all()


@router.post("/", response_model=BusinessHourOut)
def create_business_hour(bh: BusinessHourCreate, db: Session = Depends(get_db)):
    db_bh = models.BusinessHour(**bh.model_dump())
    db.add(db_bh)
    db.commit()
    db.refresh(db_bh)
    return db_bh
