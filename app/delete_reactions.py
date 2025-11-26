from database import SessionLocal
import models

TEST_USER_USERNAME = "Weakostya"  # <-- имя пользователя, чьи тесты нужно удалить
TEST_USER = "Strongostya"

def delete_reactions_tests():
    db = SessionLocal()

    try:
        # Ищем пользователя
        user = db.query(models.User).filter(models.User.username == TEST_USER_USERNAME).first()

        if not user:
            print(f"❌ Пользователь '{TEST_USER_USERNAME}' не найден")
            return

        # Удаляем его тесты
        deleted_count = (
            db.query(models.ReactionsTestResult)
            .filter(models.ReactionsTestResult.user_id == user.id)
            .delete(synchronize_session=False)
        )

        db.commit()

        print(f"🗑 Удалено {deleted_count} записей ReactionsTestResult для пользователя '{TEST_USER_USERNAME}'")

    finally:
        db.close()

def delete_reactions():
    db = SessionLocal()

    try:
        # Ищем пользователя
        user = db.query(models.User).filter(models.User.username == TEST_USER).first()

        if not user:
            print(f"❌ Пользователь '{TEST_USER}' не найден")
            return

        # Удаляем его тесты
        deleted_count = (
            db.query(models.ReactionsTestResult)
            .filter(models.ReactionsTestResult.user_id == user.id)
            .delete(synchronize_session=False)
        )

        db.commit()

        print(f"🗑 Удалено {deleted_count} записей ReactionsTestResult для пользователя '{TEST_USER}'")

    finally:
        db.close()


delete_reactions_tests()
delete_reactions()