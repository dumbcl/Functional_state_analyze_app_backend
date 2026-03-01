from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database, auth
from app.database import SessionLocal, get_db
from sqlalchemy import func
import random

router = APIRouter()


@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db), author: models.User = Depends(auth.get_current_user)):
    if not user.username or user.username.strip() == "":
        max_id = db.query(func.max(models.User.id)).scalar() or 0
        user.username = str(max_id + 1)
    else:
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            return {"error_msg": "USERNAME_ALREADY_REGISTERED"}

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        nickname=user.nickname,
        name=user.name,
        surname=user.surname,
        weight=user.weight,
        height=user.height,
        gender=user.gender,
        type=user.type,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = auth.create_access_token(data={"sub": new_user.username})

    if user.silent_creation:
        test = models.Trainees(
            trainer_id=author.id,
            trainee_id=new_user.id,
        )
        db.add(test)
        db.commit()
        db.refresh(test)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.Token)
def admin_update_password(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user:
        return {"error_msg": "USERNAME_NOT_EXISTS"}

    db_user.hashed_password = auth.get_password_hash(user.password)
    db.commit()

    return {"status": "PASSWORD_UPDATED_SUCCESSFULLY"}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password) or db_user.type != user.type:
        return {"error_msg": "LOGIN_OR_PASSWORD_INCORRECT"}
    access_token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer", "nickname": db_user.nickname}

@router.post("/login-code", response_model=schemas.Token)
def login(code: schemas.CodeCreate, db: Session = Depends(get_db)):
    db_testing = db.query(models.TraineeTestings).filter(models.TraineeTestings.code == code.code).first()
    if not db_testing:
        return {"error_msg": "CODE_INCORRECT"}
    db_user = db.query(models.User).filter(models.User.id ==db_testing.user_id).first()
    access_token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer", "nickname": db_user.nickname}

@router.post("/start-test")
def start_test(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):

    test = models.TraineeTestings(
        user_id=user.id,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"new_test_id": test.id}

@router.post("/create-testing")
def create_testing(
    testing: schemas.TraineeTestings,
    db: Session = Depends(get_db),
    response_model=schemas.CreateTestingResponse,
):
    max_id = db.query(func.max(models.TraineeTestings.id)).scalar() or 0
    test = models.TraineeTestings(
        user_id=testing.user_id,
        mode_index=testing.mode_index,
        pressure1=testing.pressure1,
        pressure2=testing.pressure2,
        pulse=testing.pulse,
        height=testing.height,
        weight=testing.weight,
        comments=testing.comments,
        code=str(max_id) + str(random.randint(10, 99))
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return schemas.CreateTestingResponse(code = test.code)

@router.post("/start-test-find")
def start_test_find(
    code: str,
    db: Session = Depends(get_db),
):

    testing = db.query(models.TraineeTestings).filter(models.TraineeTestings.code == code).first()
    testing.has_started = True
    db.commit()
    return {"new_test_id": testing.id}

@router.get("/profile-info")
def start_test_find(
    user_id: int,
    db: Session = Depends(get_db),
    response_model=schemas.ProfileInfo
):

    user = db.query(models.TraineeTestings).filter(models.User.id == user_id).first()
    if not user:
        return schemas.ProfileInfo()

    return schemas.ProfileInfo(
        height = user.height,
        weight = user.weight
    )