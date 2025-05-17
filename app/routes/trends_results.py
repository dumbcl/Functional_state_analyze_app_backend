from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, auth, database
from app.database import get_db
from app.outside_logic.fs_score import evaluate_shtange, evaluate_personal_report, evaluate_pulse, evaluate_rufie, \
    evaluate_strup, evaluate_gench, evaluate_reactions, evaluate_text_audition, evaluate_escal_daily
from app.schemas import TrendTestResult, ShtangeTestResult, PersonalReportTestResult, PulseMeasurementResult, \
    RufieTestResult, StrupTestResult, GenchTestResult, ReactionsTestResult, TextAuditionTestResult, EscalDailyTestResult

router = APIRouter()

@router.get("/trend-test-results", response_model=TrendTestResult)
def get_trend_test_results(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    # Shtange
    shtange_objs = db.query(models.ShtangeTestResult).filter_by(user_id=user.id).order_by(models.ShtangeTestResult.test_date).all()
    shtange_test_result = [
        evaluate_shtange(
            shtange_result=obj.result_estimation,
            shtange_result_indicator=obj.reaction_indicator,
            shtange_average=db.query(func.avg(models.ShtangeTestResult.reaction_indicator)).filter_by(user_id=user.id).scalar(),
        )
        for obj in shtange_objs
    ] or None

    # PersonalReport
    personal_report_objs = db.query(models.PersonalReportTestResult).filter_by(user_id=user.id).order_by(models.PersonalReportTestResult.test_date).all()
    all_perf = [o.performance_measure for o in personal_report_objs]
    avg_perf = sum(all_perf) / len(all_perf) if all_perf else None
    personal_report = [
        evaluate_personal_report(
            report_text=obj.days_comparison,
            report_current=obj.performance_measure,
            report_average=avg_perf,
        )
        for obj in personal_report_objs
    ] or None

    # PulseMeasurement
    pulse_objs = db.query(models.PulseMeasurement).filter_by(user_id=user.id).order_by(models.PulseMeasurement.created_at).all()
    all_pulse_values = [o.value for o in pulse_objs]
    pulse_alltime_avg = sum(all_pulse_values) / len(all_pulse_values) if all_pulse_values else None
    pulse_measurement = [
        evaluate_pulse(
            pulse_avg=obj.value,    # Здесь value — это значение в конкретном измерении
            pulse_max=obj.value,    # Либо если одно измерение — значение будет и max, min, avg
            pulse_min=obj.value,
            pulse_alltime_avg=pulse_alltime_avg,
        )
        for obj in pulse_objs
    ] or None

    # Rufie
    rufie_objs = db.query(models.RufieTestResult).filter_by(user_id=user.id).order_by(models.RufieTestResult.test_date).all()
    all_rufie = [o.rufie_index for o in rufie_objs if o.rufie_index is not None]
    avg_rufie = sum(all_rufie) / len(all_rufie) if all_rufie else None
    rufie_test_result = [
        evaluate_rufie(
            rufie_result=obj.result_estimation,
            rufie_indicator=obj.rufie_index,
            rufie_avg=avg_rufie,
        )
        for obj in rufie_objs
    ] or None

    # Strup
    strup_objs = db.query(models.StrupTestResult).filter_by(user_id=user.id).order_by(models.StrupTestResult.test_date).all()
    all_strup = [o.result for o in strup_objs if o.result is not None]
    avg_strup = sum(all_strup) / len(all_strup) if all_strup else None
    strup_test_result = [
        evaluate_strup(
            strup_result=obj.result,
            strup_avg=avg_strup,
            strup_result_estimation=obj.result_estimation,
        )
        for obj in strup_objs
    ] or None

    # Gench
    gench_objs = db.query(models.GenchTestResult).filter_by(user_id=user.id).order_by(models.GenchTestResult.test_date).all()
    all_gench = [o.reaction_indicator for o in gench_objs if o.reaction_indicator is not None]
    avg_gench = sum(all_gench) / len(all_gench) if all_gench else None
    gench_test_result = [
        evaluate_gench(
            gench_indicator=obj.reaction_indicator,
            gench_result_estimation=obj.result_estimation,
            gench_avg=avg_gench,
        )
        for obj in gench_objs
    ] or None

    # Reactions
    reactions_objs = db.query(models.ReactionsTestResult).filter_by(user_id=user.id).order_by(models.ReactionsTestResult.test_date).all()
    all_visual = [o.visual_errors for o in reactions_objs if o.visual_errors is not None]
    all_audio = [o.audio_errors for o in reactions_objs if o.audio_errors is not None]
    avg_visual = sum(all_visual) / len(all_visual) if all_visual else None
    avg_audio = sum(all_audio) / len(all_audio) if all_audio else None
    reactions_test_result = [
        evaluate_reactions(
            visual=obj.visual_errors,
            audio=obj.audio_errors,
            visual_avg=avg_visual,
            audio_avg=avg_audio,
            reactions_audio_diff_avg=obj.audio_average_diff,
            reactions_visual_diff_avg=obj.visual_average_diff,
            reactions_audio_std_avg=obj.audio_quav_diff,
            reactions_visual_std_avg=obj.visual_quav_diff,
        )
        for obj in reactions_objs
    ] or None

    # TextAudition
    text_objs = db.query(models.TextAuditionResults).filter_by(user_id=user.id).order_by(models.TextAuditionResults.test_date).all()
    all_pauses_read = [o.pauses_count_read for o in text_objs if o.pauses_count_read is not None]
    all_pauses_repeat = [o.pauses_count_repeat for o in text_objs if o.pauses_count_repeat is not None]
    all_vol_read = [o.average_volume_read for o in text_objs if o.average_volume_read is not None]
    all_vol_repeat = [o.average_volume_repeat for o in text_objs if o.average_volume_repeat is not None]
    all_quality_read = [o.quality_score_read for o in text_objs if o.quality_score_read is not None]
    all_quality_repeat = [o.quality_score_repeat for o in text_objs if o.quality_score_repeat is not None]
    avg_pauses_read = sum(all_pauses_read) / len(all_pauses_read) if all_pauses_read else None
    avg_pauses_repeat = sum(all_pauses_repeat) / len(all_pauses_repeat) if all_pauses_repeat else None
    avg_vol_read = sum(all_vol_read) / len(all_vol_read) if all_vol_read else None
    avg_vol_repeat = sum(all_vol_repeat) / len(all_vol_repeat) if all_vol_repeat else None
    avg_quality_read = sum(all_quality_read) / len(all_quality_read) if all_quality_read else None
    avg_quality_repeat = sum(all_quality_repeat) / len(all_quality_repeat) if all_quality_repeat else None

    text_audition_test_result = [
        evaluate_text_audition(
            pauses_read=obj.pauses_count_read,
            pauses_read_avg=avg_pauses_read,
            pauses_repeat=obj.pauses_count_repeat,
            pauses_repeat_avg=avg_pauses_repeat,
            vol_read=obj.average_volume_read,
            vol_repeat=obj.average_volume_repeat,
            vol_read_avg=avg_vol_read,
            vol_repeat_avg=avg_vol_repeat,
            quality_score_read=obj.quality_score_read,
            quality_score_repeat=obj.quality_score_repeat,
            quality_score_read_avg=avg_quality_read,
            quality_score_repeat_avg=avg_quality_repeat,
        )
        for obj in text_objs
    ] or None

    # EscalDaily
    escal_objs = db.query(models.EscalDailyResults).filter_by(user_id=user.id).order_by(models.EscalDailyResults.test_date).all()
    escal_daily_test_result = [
        evaluate_escal_daily(
            performance=obj.performance,
            fatigue=obj.fatigue,
            anxiety=obj.anxiety,
            conflict=obj.conflict,
            sanX=obj.sanX,
            sanZ=obj.sanZ,
        )
        for obj in escal_objs
    ] or None

    # Вернуть агрегированный результат
    return TrendTestResult(
        shtange_test_result=shtange_test_result,
        personal_report=personal_report,
        pulse_measurement=pulse_measurement,
        rufie_test_result=rufie_test_result,
        strup_test_result=strup_test_result,
        gench_test_result=gench_test_result,
        reactions_test_result=reactions_test_result,
        text_audition_test_result=text_audition_test_result,
        escal_daily_test_result=escal_daily_test_result,
    )