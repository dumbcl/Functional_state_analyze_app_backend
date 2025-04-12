from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from app import models, schemas, database, auth
from app.database import SessionLocal
from fastapi import HTTPException
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/pulse")
def add_pulse(data: List[schemas.PulseIn], db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    new_entries = []
    for entry in data:
        exists = db.query(models.PulseMeasurement).filter_by(user_id=user.id, measured_at=entry.measured_at).first()
        if not exists:
            new_entry = models.PulseMeasurement(
                user_id=user.id,
                value=entry.value,
                measured_at=entry.measured_at
            )
            new_entries.append(new_entry)
    db.add_all(new_entries)
    db.commit()
    return {"inserted": len(new_entries)}

@router.get("/pulse", response_model=List[schemas.PulseResponse])
def get_pulse(from_: datetime = Query(None), to: datetime = Query(None), db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    to = to or datetime.utcnow()
    from_ = from_ or (to - timedelta(days=14))
    results = db.query(models.PulseMeasurement).filter(
        models.PulseMeasurement.user_id == user.id,
        models.PulseMeasurement.measured_at.between(from_, to)
    ).order_by(models.PulseMeasurement.measured_at).all()
    return results

@router.post("/shtange-test")
def add_shtange_test(data: schemas.ShtangeTestIn, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    test = models.ShtangeTestResult(
        user_id=user.id,
        heart_rate_before=data.heart_rate_before,
        breath_hold_seconds=data.breath_hold_seconds,
        heart_rate_after=data.heart_rate_after
    )
    db.add(test)
    db.commit()
    return {"status": "added"}

@router.post("/escal-test")
def add_escal_test(data: schemas.EscalTestIn, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    test = models.EscalTestResult(
        user_id=user.id,
        result_text=data.result_text
    )
    db.add(test)
    db.commit()
    return {"status": "added"}

@router.get("/available-tests", response_model=List[schemas.AvailableTest])
def get_available_tests(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    today = date.today()
    active_tests = db.query(models.Test).filter_by(user_id=user.id, is_active=True).all()
    available = []
    for test in active_tests:
        if test.type == "shtange":
            exists = db.query(models.ShtangeTestResult).filter_by(user_id=user.id, test_date=today).first()
        elif test.type == "escal":
            exists = db.query(models.EscalTestResult).filter_by(user_id=user.id, test_date=today).first()
        else:
            exists = True
        if not exists:
            available.append(schemas.AvailableTest(type=test.type))
    return available
