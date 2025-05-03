from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, auth, database
from app.schemas import DailyTestResult

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/daily-test-results", response_model=List[DailyTestResult])
def get_daily_test_results(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    # Получаем все уникальные даты, когда пользователь проходил тесты
    unique_test_dates = db.query(models.ShtangeTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    unique_test_dates += db.query(models.PersonalReportTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    unique_test_dates += db.query(models.PulseMeasurement.measured_at).filter_by(user_id=user.id).distinct().all()
    unique_test_dates += db.query(models.RufieTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    unique_test_dates += db.query(models.StrupTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    unique_test_dates += db.query(models.GenchTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    unique_test_dates += db.query(models.ReactionsTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    unique_test_dates += db.query(models.TextAuditionResults.test_date).filter_by(user_id=user.id).distinct().all()

    # Убираем дублированные даты
    unique_test_dates = list(set([date[0] for date in unique_test_dates]))

    daily_results = []

    for test_date in unique_test_dates:
        # Запрашиваем результаты из разных таблиц для конкретной даты
        shtange_results = db.query(models.ShtangeTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        shtange_result = shtange_results[0].result_estimation if shtange_results else ""
        shtange_result_indicator = shtange_results[0].reaction_indicator if shtange_results else 0
        shtange_test_result_indicator_average = db.query(func.avg(models.ShtangeTestResult.reaction_indicator)).filter_by(user_id=user.id).scalar() or 0

        # PersonalReportTestResult для этого дня
        personal_report_result = db.query(models.PersonalReportTestResult).filter_by(user_id=user.id, test_date=test_date).first()
        personal_report = personal_report_result.days_comparison if personal_report_result else ""

        # PulseMeasurement для этого дня
        pulse_measurements = db.query(models.PulseMeasurement).filter_by(user_id=user.id, measured_at=test_date).all()
        pulseAverage = sum([pm.value for pm in pulse_measurements]) / len(pulse_measurements) if pulse_measurements else 0
        pulseMax = max([pm.value for pm in pulse_measurements], default=0)
        pulseMin = min([pm.value for pm in pulse_measurements], default=0)

        # RufieTestResult для этого дня
        rufie_results = db.query(models.RufieTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        rufie_result = rufie_results[0].result_estimation if rufie_results else ""
        rufie_result_indicator = rufie_results[0].rufie_index if rufie_results else 0
        rufie_test_result_indicator_average = db.query(func.avg(models.RufieTestResult.rufie_index)).filter_by(user_id=user.id).scalar() or 0

        # StrupTestResult для этого дня
        strup_results = db.query(models.StrupTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        strup_result_estimation = strup_results[0].result_estimation if strup_results else ""
        strup_result = strup_results[0].result if strup_results else 0
        strup_test_result_average = db.query(func.avg(models.StrupTestResult.result)).filter_by(user_id=user.id).scalar() or 0

        # GenchTestResult для этого дня
        gench_results = db.query(models.GenchTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        gench_result_estimation = gench_results[0].result_estimation if gench_results else ""
        gench_result_indicator = gench_results[0].reaction_indicator if gench_results else 0
        gench_test_result_indicator_average = db.query(func.avg(models.GenchTestResult.reaction_indicator)).filter_by(user_id=user.id).scalar() or 0

        # ReactionsTestResult для этого дня
        reactions_results = db.query(models.ReactionsTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        reactions_visual_errors = reactions_results[0].visual_errors if reactions_results else 0
        reactions_audio_errors = reactions_results[0].audio_errors if reactions_results else 0
        reactions_visual_errors_average = db.query(func.avg(models.ReactionsTestResult.visual_errors)).filter_by(user_id=user.id).scalar() or 0
        reactions_audio_errors_average = db.query(func.avg(models.ReactionsTestResult.audio_errors)).filter_by(user_id=user.id).scalar() or 0

        # TextAuditionResults для этого дня
        text_audition_results = db.query(models.TextAuditionResults).filter_by(user_id=user.id, test_date=test_date).all()
        pauses_count_read = text_audition_results[0].pauses_count_read if text_audition_results else 0
        pauses_count_repeat = text_audition_results[0].pauses_count_repeat if text_audition_results else 0
        pauses_count_read_average = db.query(func.avg(models.TextAuditionResults.pauses_count_read)).filter_by(user_id=user.id).scalar() or 0
        pauses_count_repeat_average = db.query(func.avg(models.TextAuditionResults.pauses_count_repeat)).filter_by(user_id=user.id).scalar() or 0
        average_volume_read = text_audition_results[0].average_volume_read if text_audition_results else 0
        average_volume_repeat = text_audition_results[0].average_volume_repeat if text_audition_results else 0
        average_volume_read_average = db.query(func.avg(models.TextAuditionResults.average_volume_read)).filter_by(user_id=user.id).scalar() or 0
        average_volume_repeat_average = db.query(func.avg(models.TextAuditionResults.average_volume_repeat)).filter_by(user_id=user.id).scalar() or 0

        # Собираем результаты в одном объекте
        result = DailyTestResult(
            date=test_date,
            shtange_result=shtange_result,
            shtange_result_indicator=shtange_result_indicator,
            shtange_test_result_indicator_average=shtange_test_result_indicator_average,
            personal_report=personal_report,
            pulseAverage=pulseAverage,
            pulseMax=pulseMax,
            pulseMin=pulseMin,
            rufie_result=rufie_result,
            rufie_result_indicator=rufie_result_indicator,
            rufie_test_result_indicator_average=rufie_test_result_indicator_average,
            strup_result_estimation=strup_result_estimation,
            strup_result=strup_result,
            strup_test_result_average=strup_test_result_average,
            gench_result_estimation=gench_result_estimation,
            gench_result_indicator=gench_result_indicator,
            gench_test_result_indicator_average=gench_test_result_indicator_average,
            reactions_visual_errors=reactions_visual_errors,
            reactions_audio_errors=reactions_audio_errors,
            reactions_visual_errors_average=reactions_visual_errors_average,
            reactions_audio_errors_average=reactions_audio_errors_average,
            pauses_count_read=pauses_count_read,
            pauses_count_repeat=pauses_count_repeat,
            pauses_count_read_average=pauses_count_read_average,
            pauses_count_repeat_average=pauses_count_repeat_average,
            average_volume_read=average_volume_read,
            average_volume_repeat=average_volume_repeat,
            average_volume_read_average=average_volume_read_average,
            average_volume_repeat_average=average_volume_repeat_average,
            day_description="",
            day_type="GOOD",  # Заглушка
        )

        daily_results.append(result)

    return daily_results
