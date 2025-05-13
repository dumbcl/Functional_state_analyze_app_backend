# app/routes/rufie_test.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, auth
from app.database import get_db

router = APIRouter()

@router.post("/rufie-test")
def create_rufie_test(
    data: schemas.RufieTestResultCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    rufie_index = models.RufieTestResult.calculate_rufie_index(
        data.measurement_first, data.measurement_second, data.measurement_third
    )
    result_estimation = models.RufieTestResult.calculate_result_estimation(rufie_index)

    test = models.RufieTestResult(
        user_id=user.id,
        measurement_first=data.measurement_first,
        measurement_second=data.measurement_second,
        measurement_third=data.measurement_third,
        rufie_index=rufie_index,
        result_estimation=result_estimation
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"status": "added"}
