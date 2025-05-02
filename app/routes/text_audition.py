import random
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
import os
from app import models, schemas, database, auth
from pathlib import Path
import shutil

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Пример двух списков с текстами
read_list = [
    "This is the first text from list 1.",
    "Another text from list 1.",
    "Yet another text from list 1."
]

repeat_list = [
    "Here comes the first text from list 2.",
    "Another text from list 2.",
    "This is a sample text from list 2."
]

@router.get("/text-for-auditions", response_model=schemas.TextAuditionResponse)
def get_texts_for_auditions():
    # Выбираем случайный элемент из каждого списка
    read_text = random.choice(read_list)
    repeat_text = random.choice(repeat_list)

    # Отправляем их в ответ
    return schemas.TextAuditionResponse(
        read_text=read_text,
        repeat_text=repeat_text
    )

@router.post("/text-audition-result", response_model=schemas.TextAuditionResultResponse)
async def upload_audio_files(
    read_text_file: UploadFile = File(...),
    repeat_text_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    try:
        upload_folder = "uploads/audio_files"
        Path(upload_folder).mkdir(parents=True, exist_ok=True)

        # Сохранение первого файла
        read_text_file_path = os.path.join(upload_folder, read_text_file.filename)
        with open(read_text_file_path, "wb") as buffer:
            shutil.copyfileobj(read_text_file.file, buffer)

        # Сохранение второго файла
        repeat_text_file_path = os.path.join(upload_folder, repeat_text_file.filename)
        with open(repeat_text_file_path, "wb") as buffer:
            shutil.copyfileobj(repeat_text_file.file, buffer)

        # Сохраняем информацию в базе данных
        text_audition_result = models.TextAuditionResults(
            user_id=user.id,
            read_text_file_path=read_text_file_path,
            repeat_text_file_path=repeat_text_file_path
        )
        db.add(text_audition_result)
        db.commit()
        db.refresh(text_audition_result)

        return text_audition_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))