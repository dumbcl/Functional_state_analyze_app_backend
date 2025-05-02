# app/routes/reactions_test.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, auth
import json

router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/reactions-test", response_model=schemas.ReactionsTestResultsResponse)
def create_reactions_test(
        data: schemas.ReactionsTestResultsCreate,
        db: Session = Depends(get_db),
        user: models.User = Depends(auth.get_current_user)
):
    # Преобразуем списки пар в строку JSON
    visual_reactions = json.dumps(data.visual)
    audio_reactions = json.dumps(data.audio)

    # Высчитываем количество ошибок
    visual_errors = models.ReactionsTestResult.calculate_errors(data.visual)
    audio_errors = models.ReactionsTestResult.calculate_errors(data.audio)

    # Создаём запись в базе данных
    test = models.ReactionsTestResult(
        user_id=user.id,
        visual=visual_reactions,
        audio=audio_reactions,
        visual_errors=visual_errors,
        audio_errors=audio_errors
    )

    db.add(test)
    db.commit()
    db.refresh(test)
    return test
