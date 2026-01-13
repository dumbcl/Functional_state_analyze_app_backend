from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, auth
from app.database import get_db
from app.schemas import Trainee
from typing import List

router = APIRouter()

@router.post("/add-trainee")
def add_trainee(
    data: schemas.TraineeRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    db_user = db.query(models.User).filter(models.User.username == data.username).first()
    if not db_user or not db_user.type == "ATHLETE":
        return {"error_msg": "USERNAME_NOT_EXIST"}
    test = models.Trainees(
        trainer_id=user.id,
        trainee_id=db_user.id,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"status": "added"}


@router.get("/get_trainees", response_model=List[Trainee])
def get_trainees(
        db: Session = Depends(get_db),
        user: models.User = Depends(auth.get_current_user)
) :
    # Получаем все связи где текущий пользователь является тренером
    trainees = db.query(models.User).join(
        models.Trainees,
        models.Trainees.trainee_id == models.User.id
    ).filter(
        models.Trainees.trainer_id == user.id
    ).all()

    # Формируем список ответа
    result = []
    for trainee in trainees:
        result.append(Trainee(
            user_id=trainee.id,
            username=trainee.username,
            nickname=trainee.nickname,
            name=trainee.name,
            surname=trainee.surname,
        ))

    return result

@router.delete("/delete-trainee")
def delet_trainee(
        data: schemas.TraineeRequest,
        db: Session = Depends(get_db),
        user: models.User = Depends(auth.get_current_user)
):
    # Находим пользователя по username
    db_user = db.query(models.User).filter(models.User.username == data.username).first()
    if not db_user:
        return {"error_msg": "USERNAME_NOT_EXIST"}

    # Находим связь между тренером и trainee
    trainee_relation = db.query(models.Trainees).filter(
        models.Trainees.trainer_id == user.id,
        models.Trainees.trainee_id == db_user.id
    ).first()

    if not trainee_relation:
        return {"error_msg": "TRAINEE_NOT_FOUND"}

    # Удаляем связь
    db.delete(trainee_relation)
    db.commit()

    return {"status": "deleted"}