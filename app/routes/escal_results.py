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

@router.post("/escal-results")
def create_escal_results(
    results: schemas.EscalResultsCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    db_results = models.EscalResults(user_id=user.id, **results.dict())
    db.add(db_results)
    db.commit()
    db.refresh(db_results)
    return {"status": "added"}

@router.get("/escal-results", response_model=schemas.EscalResultsResponse)
def get_escal_results(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    db_results = db.query(models.EscalResults).filter(models.EscalResults.user_id == user.id).first()
    if db_results is None:
        raise HTTPException(status_code=404, detail="Results not found for this user")
    return db_results