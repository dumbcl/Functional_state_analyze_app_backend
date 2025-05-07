# app/routes/gench_test.py
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


@router.post("/gench-test")
def create_gench_test(
        data: schemas.GenchTestResultCreate,
        db: Session = Depends(get_db),
        user: models.User = Depends(auth.get_current_user)
):
    result_estimation = models.GenchTestResult.calculate_result_estimation(data.breath_hold_seconds)
    reaction_indicator = models.GenchTestResult.calculate_reaction_indicator(data.heart_rate_after,
                                                                             data.heart_rate_before)

    test = models.GenchTestResult(
        user_id=user.id,
        heart_rate_before=data.heart_rate_before,
        breath_hold_seconds=data.breath_hold_seconds,
        heart_rate_after=data.heart_rate_after,
        result_estimation=result_estimation,
        reaction_indicator=reaction_indicator
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"status": "added"}
