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
        yield SessionLocal()
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

# app/routes/health.py
@router.get("/available-tests", response_model=schemas.AvailableTestsResponse)
def get_available_tests(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    today = date.today()

    # Все возможные типы тестов
    test_types = ["shtange", "escal", "escal_daily", "gench", "reactions", "rufie", "strup", "text_audition"]
    available_tests = []
    completed_tests = []

    # Флаг для проверки, был ли пройден тест "escal"
    escal_test_completed = False

    # Проверяем, был ли пройден тест "escal"
    escal_test = db.query(models.EscalResults).filter_by(user_id=user.id).first()
    if escal_test:
        escal_test_completed = True

    # Если "escal" не пройден — возвращаем только "escal" в доступных тестах
    if not escal_test_completed:
        available_tests.append(schemas.AvailableTest(type="escal"))
        return schemas.AvailableTestsResponse(
            available_tests=available_tests,
            completed_tests=[]
        )

    # Если "escal" пройден, всегда добавляем "escal_daily" в доступные тесты
    available_tests.append(schemas.AvailableTest(type="escal_daily"))

    # Для остальных тестов проверяем, были ли они пройдены сегодня
    for test_type in test_types:
        if test_type == "escal":
            continue
        elif test_type == "escal_daily":
            continue

        exists = False  # Флаг для проверки, был ли тест пройден сегодня
        last_test_date = None  # Дата последнего прохождения

        if test_type == "shtange":
            test = db.query(models.ShtangeTestResult).filter_by(user_id=user.id).order_by(models.ShtangeTestResult.test_date.desc()).first()
            if test:
                exists = True
                last_test_date = test.test_date
        elif test_type == "escal":
            continue
        elif test_type == "escal_daily":
            continue
        elif test_type == "gench":
            test = db.query(models.GenchTestResult).filter_by(user_id=user.id).order_by(models.GenchTestResult.test_date.desc()).first()
            if test and test.test_date == today:
                exists = True
                last_test_date = test.test_date
        elif test_type == "reactions":
            test = db.query(models.ReactionsTestResult).filter_by(user_id=user.id).order_by(models.ReactionsTestResult.test_date.desc()).first()
            if test and test.test_date == today:
                exists = True
                last_test_date = test.test_date
        elif test_type == "rufie":
            test = db.query(models.RufieTestResult).filter_by(user_id=user.id).order_by(models.RufieTestResult.test_date.desc()).first()
            if test and test.test_date == today:
                exists = True
                last_test_date = test.test_date
        elif test_type == "strup":
            test = db.query(models.StrupTestResult).filter_by(user_id=user.id).order_by(models.StrupTestResult.test_date.desc()).first()
            if test and test.test_date == today:
                exists = True
                last_test_date = test.test_date
        elif test_type == "text_audition":
            test = db.query(models.TextAuditionResults).filter_by(user_id=user.id).order_by(
                models.TextAuditionResults.test_date.desc()).first()
            if test and test.test_date == today:
                exists = True
                last_test_date = test.test_date

        # Добавляем тест в нужный список
        test_data = schemas.AvailableTest(type=test_type, last_test_date=str(last_test_date))

        if exists:
            completed_tests.append(test_data)
        else:
            available_tests.append(test_data)

    return schemas.AvailableTestsResponse(
        available_tests=available_tests,
        completed_tests=completed_tests
    )

