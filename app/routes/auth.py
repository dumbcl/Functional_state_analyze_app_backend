from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database, auth
from app.database import SessionLocal, get_db

router = APIRouter()

@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/refresh", response_model=schemas.Token)
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