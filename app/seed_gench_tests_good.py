from datetime import date, datetime, timedelta

from database import SessionLocal
import models

# Задай здесь тестового пользователя
TEST_USER_EMAIL = "Strongostya"
# либо можно вместо email использовать ID:
# TEST_USER_ID = 1


def get_test_user_id(db):
    user = db.query(models.User).filter(models.User.username == TEST_USER_EMAIL).first()
    if not user:
        raise RuntimeError(f"User with email {TEST_USER_EMAIL} not found")
    return user.id


def seed_gench_tests():
    db = SessionLocal()
    try:
        user_id = get_test_user_id(db)

        # 15 дней, от более старых к более новым
        base_date = date.today() - timedelta(days=14)

        # Постепенное ухудшение показателей

        # Задержка дыхания (сек) — убывает, качество ухудшается
        breath_hold_seconds_list = [
            18, 20, 22, 24, 26,   # GOOD
            29, 32, 35, 38, 40, 42, 44,  # MEDIUM
            46, 48, 50  # BAD
        ]

        # ЧСС до пробы (слегка растёт)
        heart_rate_before_list = [
            74, 72, 72, 70, 70,
            68, 68, 66, 66, 64,
            64, 62, 62, 60, 60,
        ]

        # ЧСС после пробы — подобраны так, чтобы отношение after/before понемногу росло
        heart_rate_after_list = [
            88,  # 60 -> 63  ~1.05
            85,  # 60 -> 64  ~1.07
            84,  # 62 -> 66  ~1.06
            81,  # 62 -> 67  ~1.08
            80,  # 64 -> 70  ~1.09
            78,  # 64 -> 70  ~1.09
            77,  # 66 -> 73  ~1.11
            74,  # 66 -> 74  ~1.12
            73,  # 68 -> 77  ~1.13
            70,  # 68 -> 78  ~1.15
            70,  # 70 -> 80  ~1.14
            67,  # 70 -> 81  ~1.16
            66,  # 72 -> 84  ~1.17
            64,  # 72 -> 85  ~1.18
            63,  # 74 -> 88  ~1.19
        ]

        # Проверка на всякий случай
        assert len(breath_hold_seconds_list) == len(heart_rate_before_list) == len(heart_rate_after_list) == 15

        for i in range(15):
            heart_rate_before = heart_rate_before_list[i]
            heart_rate_after = heart_rate_after_list[i]
            breath_hold_seconds = breath_hold_seconds_list[i]

            # Используем те же методы, что и в ручке /gench-test
            result_estimation = models.GenchTestResult.calculate_result_estimation(breath_hold_seconds)
            reaction_indicator = models.GenchTestResult.calculate_reaction_indicator(
                heart_rate_after,
                heart_rate_before,
            )

            test_date = base_date + timedelta(days=i)

            test = models.GenchTestResult(
                user_id=user_id,
                heart_rate_before=heart_rate_before,
                breath_hold_seconds=breath_hold_seconds,
                heart_rate_after=heart_rate_after,
                result_estimation=result_estimation,
                reaction_indicator=reaction_indicator,
                test_date=test_date,
                created_at=datetime.utcnow(),
            )
            db.add(test)

            print(
                f"#{i+1}: date={test_date}, "
                f"before={heart_rate_before}, after={heart_rate_after}, "
                f"hold={breath_hold_seconds}, "
                f"indicator={reaction_indicator:.3f}, estimation={result_estimation}"
            )

        db.commit()
        print("✅ 15 GenchTestResult записей успешно добавлены")

    finally:
        db.close()


seed_gench_tests()