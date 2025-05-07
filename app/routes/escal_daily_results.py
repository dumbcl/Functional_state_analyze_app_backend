# app/routes/escal_daily_results.py
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

@router.post("/escal-daily-results")
def create_escal_daily_results(
    data: schemas.EscalDailyResultsCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    # Создаём запись в базе данных
    test = models.EscalDailyResults(
        user_id=user.id,
        performance=data.performance,
        fatigue=data.fatigue,
        anxiety=data.anxiety,
        conflict=data.conflict,
        autonomy=data.autonomy,
        heteron=data.heteron,
        eccentricity=data.eccentricity,
        concetration=data.concetration,
        vegeative=data.vegeative,
        wellbeingX=data.wellbeingX,
        wellbeingZ=data.wellbeingZ,
        activityX=data.activityX,
        activityZ=data.activityZ,
        moodX=data.moodX,
        moodZ=data.moodZ,
        ipX=data.ipX,
        ipZ=data.ipZ
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"status": "added"}
