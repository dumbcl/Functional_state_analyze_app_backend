# app/routes/strup_test.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, auth

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/strup-test", response_model=schemas.StrupTestResultResponse)
def create_strup_test(
    data: schemas.StrupTestResultCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    result_estimation = models.StrupTestResult.calculate_result_estimation(data.result)

    test = models.StrupTestResult(
        user_id=user.id,
        result=data.result,
        result_estimation=result_estimation
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return test
