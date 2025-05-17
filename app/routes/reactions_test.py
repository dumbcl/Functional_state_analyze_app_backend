from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, auth
import json

from app.database import get_db

router = APIRouter()

@router.post("/reactions-test")
def create_reactions_test(
        data: schemas.ReactionsTestResultsCreate,
        db: Session = Depends(get_db),
        user: models.User = Depends(auth.get_current_user)
):

    # Высчитываем количество ошибок
    visual_errors = models.ReactionsTestResult.calculate_errors(data.audio)
    audio_errors = models.ReactionsTestResult.calculate_errors(data.visual)

    audio_average_diff, audio_quav_diff = models.ReactionsTestResult.mean_std_difference(data.audio)
    visual_average_diff, visual_quav_diff = models.ReactionsTestResult.mean_std_difference(data.visual)

    # Создаём запись в базе данных
    test = models.ReactionsTestResult(
        user_id=user.id,
        visual=json.dumps(data.visual),
        audio=json.dumps(data.audio),
        visual_errors=visual_errors,
        audio_errors=audio_errors,
        visual_average_diff=visual_average_diff,
        audio_average_diff = audio_average_diff,
        visual_quav_diff = visual_quav_diff,
        audio_quav_diff = audio_quav_diff,
    )

    db.add(test)
    db.commit()
    db.refresh(test)
    return {"status": "added"}
