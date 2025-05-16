from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, auth, database
from app.database import get_db
from app.schemas import TrendTestResult, ShtangeTestResult, PersonalReportTestResult, PulseMeasurementResult, \
    RufieTestResult, StrupTestResult, GenchTestResult, ReactionsTestResult, TextAuditionTestResult, EscalDailyTestResult

router = APIRouter()

@router.get('/trend-test-results', response_model=TrendTestResult)
def get_trend_test_results(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    # Получить все результаты нужных таблиц по user_id
    shtange = db.query(models.ShtangeTestResult).filter_by(user_id=user.id).order_by(models.ShtangeTestResult.test_date).all()
    personal_report = db.query(models.PersonalReportTestResult).filter_by(user_id=user.id).order_by(models.PersonalReportTestResult.test_date).all()
    pulse = db.query(models.PulseMeasurement).filter_by(user_id=user.id).order_by(models.PulseMeasurement.created_at).all()
    rufie = db.query(models.RufieTestResult).filter_by(user_id=user.id).order_by(models.RufieTestResult.test_date).all()
    strup = db.query(models.StrupTestResult).filter_by(user_id=user.id).order_by(models.StrupTestResult.test_date).all()
    gench = db.query(models.GenchTestResult).filter_by(user_id=user.id).order_by(models.GenchTestResult.test_date).all()
    reactions = db.query(models.ReactionsTestResult).filter_by(user_id=user.id).order_by(models.ReactionsTestResult.test_date).all()
    text_audition = db.query(models.TextAuditionResults).filter_by(user_id=user.id).order_by(models.TextAuditionResults.test_date).all()
    escal = db.query(models.EscalDailyResults).filter_by(user_id=user.id).order_by(models.EscalDailyResults.test_date).all()

    # Собрать в ответ согласно schemas.TrendTestResult
    return TrendTestResult(
        shtange_test_result=[ShtangeTestResult.from_orm(x) for x in shtange] if shtange else None,
        personal_report=[PersonalReportTestResult.from_orm(x) for x in personal_report] if personal_report else None,
        pulse_measurement=[PulseMeasurementResult.from_orm(x) for x in pulse] if pulse else None,
        rufie_test_result=[RufieTestResult.from_orm(x) for x in rufie] if rufie else None,
        strup_test_result=[StrupTestResult.from_orm(x) for x in strup] if strup else None,
        gench_test_result=[GenchTestResult.from_orm(x) for x in gench] if gench else None,
        reactions_test_result=[ReactionsTestResult.from_orm(x) for x in reactions] if reactions else None,
        text_audition_test_result=[TextAuditionTestResult.from_orm(x) for x in text_audition] if text_audition else None,
        escal_daily_test_result=[EscalDailyTestResult.from_orm(x) for x in escal] if escal else None
    )