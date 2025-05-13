# app/routes/personal_report_test.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, auth
from app.database import get_db

router = APIRouter()

@router.post("/personal-report-test")
def create_personal_report_test(
    data: schemas.PersonalReportTestResultCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    test = models.PersonalReportTestResult(
        user_id=user.id,
        performance_measure=data.performance_measure,
        days_comparison=data.days_comparison
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"status": "added"}
