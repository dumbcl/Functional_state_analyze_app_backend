import json
import random
from datetime import date, datetime, timedelta

from database import SessionLocal
import models

# Задай тут тестового пользователя
TEST_USER_EMAIL = "Weakostya"
# или, если знаешь id:
# TEST_USER_ID = 1


def get_test_user_id(db):
    user = db.query(models.User).filter(models.User.username == TEST_USER_EMAIL).first()
    if not user:
        raise RuntimeError(f"User with email {TEST_USER_EMAIL} not found")
    return user.id


def generate_reaction_pairs(
    num_pairs: int,
    base_ts: int,
    target_diff_ms: int,
    jitter_ms: int,
) -> list[tuple[int, int]]:
    """
    Генерируем список пар (ожидаемое_время, фактическое_время) так,
    чтобы разность была около target_diff_ms с разбросом jitter_ms.
    """
    pairs: list[tuple[int, int]] = []
    for i in range(num_pairs):
        expected = base_ts + i * 2000  # условно, каждые 2 секунды стимул
        diff = int(random.gauss(target_diff_ms, jitter_ms))
        if diff < 0:
            diff = 0
        actual = expected + diff
        pairs.append((expected, actual))
    return pairs


def seed_reactions_tests():
    random.seed(42)  # чтобы результаты были воспроизводимы
    db = SessionLocal()
    try:
        user_id = get_test_user_id(db)

        # 15 дней от более старых к более новым
        base_date = date.today() - timedelta(days=14)

        # Постепенное ухудшение:
        # аудио: средняя разница от 250 → 900 мс
        audio_target_means = [
            250, 270, 290, 310, 330,
            360, 390, 420, 450, 500,
            550, 600, 700, 800, 900,
        ]

        # визуал: чуть лучше, но тоже ухудшается от 220 → 800 мс
        visual_target_means = [
            220, 240, 260, 280, 300,
            330, 360, 390, 420, 460,
            500, 550, 600, 700, 800,
        ]

        # Стандартное отклонение будет расти: реакции становятся более "рваными"
        target_jitters = [
            40, 45, 50, 55, 60,
            65, 70, 75, 80, 90,
            100, 110, 130, 150, 180,
        ]

        num_pairs_per_test = 20

        for i in range(15):
            test_date = base_date + timedelta(days=i)

            audio_pairs = generate_reaction_pairs(
                num_pairs=num_pairs_per_test,
                base_ts=1_000_000 + i * 100_000,
                target_diff_ms=audio_target_means[i],
                jitter_ms=target_jitters[i],
            )

            visual_pairs = generate_reaction_pairs(
                num_pairs=num_pairs_per_test,
                base_ts=2_000_000 + i * 100_000,
                target_diff_ms=visual_target_means[i],
                jitter_ms=target_jitters[i],
            )

            # Считаем метрики теми же методами, что и в эндпоинте
            audio_average_diff, audio_quav_diff = models.ReactionsTestResult.mean_std_difference(audio_pairs)
            visual_average_diff, visual_quav_diff = models.ReactionsTestResult.mean_std_difference(visual_pairs)

            # Ошибки: разница > 1000 мс
            audio_errors = models.ReactionsTestResult.calculate_errors(audio_pairs)
            visual_errors = models.ReactionsTestResult.calculate_errors(visual_pairs)

            test = models.ReactionsTestResult(
                user_id=user_id,
                visual=json.dumps(visual_pairs),
                audio=json.dumps(audio_pairs),
                visual_errors=visual_errors,
                audio_errors=audio_errors,
                visual_average_diff=visual_average_diff,
                audio_average_diff=audio_average_diff,
                visual_quav_diff=visual_quav_diff,
                audio_quav_diff=audio_quav_diff,
                test_date=test_date,
                created_at=datetime.utcnow(),
            )

            db.add(test)

            print(
                f"#{i+1}: date={test_date}, "
                f"audio_mean={audio_average_diff:.1f}, audio_std={audio_quav_diff:.1f}, audio_err={audio_errors}, "
                f"visual_mean={visual_average_diff:.1f}, visual_std={visual_quav_diff:.1f}, visual_err={visual_errors}"
            )
        db.commit()
        print("✅ 15 ReactionsTestResult записей успешно добавлены")

    finally:
        db.close()

seed_reactions_tests()