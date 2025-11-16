from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, auth, database
from app.database import get_db
from app.outside_logic.fs_score import evaluate_shtange, evaluate_personal_report, evaluate_pulse, evaluate_rufie, \
    evaluate_strup, evaluate_gench, evaluate_reactions, evaluate_text_audition, evaluate_escal_daily, calculate_fs_score
from app.schemas import TrendTestResult, ShtangeTestResult, PersonalReportTestResult, PulseMeasurementResult, \
    RufieTestResult, StrupTestResult, GenchTestResult, ReactionsTestResult, TextAuditionTestResult, \
    EscalDailyTestResult, DailyEstimationResult, LastGenchResult, LastShtangeResult, LastReactionsResult, GenchDailyResults, ShtangeDailyResults, ReactionsAvgDailyResult

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
            date=str(obj.test_date)
        )
        for obj in shtange_objs
    ]
    shtange_test_result = [r for r in shtange_test_result if r is not None] or None
    if not shtange_test_result:
        shtange_test_result = None

    # PersonalReport
    personal_report_objs = db.query(models.PersonalReportTestResult).filter_by(user_id=user.id).order_by(models.PersonalReportTestResult.test_date).all()
    all_perf = [o.performance_measure for o in personal_report_objs]
    avg_perf = sum(all_perf) / len(all_perf) if all_perf else None
    personal_report = [
        evaluate_personal_report(
            report_text=obj.days_comparison,
            report_current=obj.performance_measure,
            report_average=avg_perf,
            date=str(obj.test_date)
        )
        for obj in personal_report_objs
    ]
    personal_report = [r for r in personal_report if r is not None] or None
    if not personal_report:
        personal_report = None

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
            date=str(obj.created_at),
        )
        for obj in pulse_objs
    ]
    pulse_measurement = [r for r in pulse_measurement if r is not None] or None
    if not pulse_measurement:
        pulse_measurement = None

    # Rufie
    rufie_objs = db.query(models.RufieTestResult).filter_by(user_id=user.id).order_by(models.RufieTestResult.test_date).all()
    all_rufie = [o.rufie_index for o in rufie_objs if o.rufie_index is not None]
    avg_rufie = sum(all_rufie) / len(all_rufie) if all_rufie else None
    rufie_test_result = [
        evaluate_rufie(
            rufie_result=obj.result_estimation,
            rufie_indicator=obj.rufie_index,
            rufie_avg=avg_rufie,
            date=str(obj.test_date)
        )
        for obj in rufie_objs
    ]
    rufie_test_result = [r for r in rufie_test_result if r is not None] or None
    if not rufie_test_result:
        rufie_test_result = None

    # Strup
    strup_objs = db.query(models.StrupTestResult).filter_by(user_id=user.id).order_by(models.StrupTestResult.test_date).all()
    all_strup = [o.result for o in strup_objs if o.result is not None]
    avg_strup = sum(all_strup) / len(all_strup) if all_strup else None
    strup_test_result = [
        evaluate_strup(
            strup_result=obj.result,
            strup_avg=avg_strup,
            strup_result_estimation=obj.result_estimation,
            date=str(obj.test_date)
        )
        for obj in strup_objs
    ]
    strup_test_result= [r for r in strup_test_result if r is not None] or None
    if not strup_test_result:
        strup_test_result = None

    # Gench
    gench_objs = db.query(models.GenchTestResult).filter_by(user_id=user.id).order_by(models.GenchTestResult.test_date).all()
    all_gench = [o.reaction_indicator for o in gench_objs if o.reaction_indicator is not None]
    avg_gench = sum(all_gench) / len(all_gench) if all_gench else None
    gench_test_result = [
        evaluate_gench(
            gench_indicator=obj.reaction_indicator,
            gench_result_estimation=obj.result_estimation,
            gench_avg=avg_gench,
            date=str(obj.test_date)
        )
        for obj in gench_objs
    ]
    gench_test_result = [r for r in gench_test_result if r is not None] or None
    if not gench_test_result:
        gench_test_result = None

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
            date=str(obj.test_date)
        )
        for obj in reactions_objs
    ]
    reactions_test_result = [r for r in reactions_test_result if r is not None] or None
    if not reactions_test_result:
        reactions_test_result = None

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
            date=str(obj.test_date),
        )
        for obj in text_objs
    ]
    text_audition_test_result = [r for r in text_audition_test_result if r is not None] or None
    if not text_audition_test_result:
        text_audition_test_result = None

    # EscalDaily
    escal_objs = db.query(models.EscalDailyResults).filter_by(user_id=user.id).order_by(models.EscalDailyResults.test_date).all()
    escal_daily_test_result = [
        evaluate_escal_daily(
            performance=obj.performance,
            fatigue=obj.fatigue,
            anxiety=obj.anxiety,
            conflict=obj.conflict,
            sanX=obj.ipX,
            sanZ=obj.ipZ,
            date=str(obj.test_date),
        )
        for obj in escal_objs
    ]
    escal_daily_test_result = [r for r in escal_daily_test_result if r is not None] or None
    if not escal_daily_test_result:
        escal_daily_test_result = None

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
        estimation_result=get_fs_categories_by_date(db, user),
    )


def get_fs_categories_by_date(db: Session, user: models.User) -> List[DailyEstimationResult]:
    # Сбор всех дат
    test_dates = []
    test_dates += db.query(models.ShtangeTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    test_dates += db.query(models.PersonalReportTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    test_dates += db.query(models.RufieTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    test_dates += db.query(models.StrupTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    test_dates += db.query(models.GenchTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    test_dates += db.query(models.ReactionsTestResult.test_date).filter_by(user_id=user.id).distinct().all()
    test_dates += db.query(models.TextAuditionResults.test_date).filter_by(user_id=user.id).distinct().all()

    unique_test_dates = list(set([d[0] for d in test_dates if d and d[0]]))
    unique_test_dates.sort()

    fs_score_list = []
    for test_date in unique_test_dates:
        # Здесь копируй из своего эндпоинта блок получения всех данных на этот день
        shtange_results = db.query(models.ShtangeTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        shtange_result_indicator = shtange_results[0].reaction_indicator if shtange_results else None
        shtange_test_result_indicator_average = db.query(func.avg(models.ShtangeTestResult.reaction_indicator)).filter_by(user_id=user.id).scalar()

        personal_report_result = db.query(models.PersonalReportTestResult).filter_by(user_id=user.id, test_date=test_date).first()
        personal_report_indicator = personal_report_result.performance_measure if personal_report_result else None
        personal_report_all = db.query(models.PersonalReportTestResult).filter_by(user_id=user.id).all()
        personal_report_indicator_average = sum([pm.performance_measure for pm in personal_report_all]) / len(personal_report_all) if personal_report_all else None

        pulse_measurements = db.query(models.PulseMeasurement).filter_by(user_id=user.id, created_at=test_date).all()
        pulseAverage = sum([pm.value for pm in pulse_measurements]) / len(pulse_measurements) if pulse_measurements else None
        pulse_alltime_measurements = db.query(models.PulseMeasurement).filter_by(user_id=user.id).all()
        pulse_alltime_average = sum([pm.value for pm in pulse_alltime_measurements]) / len(pulse_alltime_measurements) if pulse_alltime_measurements else None

        rufie_results = db.query(models.RufieTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        rufie_result_indicator = rufie_results[0].rufie_index if rufie_results else None
        rufie_test_result_indicator_average = db.query(func.avg(models.RufieTestResult.rufie_index)).filter_by(user_id=user.id).scalar()

        strup_results = db.query(models.StrupTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        strup_result = strup_results[0].result if strup_results else None
        strup_test_result_average = db.query(func.avg(models.StrupTestResult.result)).filter_by(user_id=user.id).scalar()

        gench_results = db.query(models.GenchTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        gench_result_indicator = gench_results[0].reaction_indicator if gench_results else None
        gench_test_result_indicator_average = db.query(func.avg(models.GenchTestResult.reaction_indicator)).filter_by(user_id=user.id).scalar()

        reactions_results = db.query(models.ReactionsTestResult).filter_by(user_id=user.id, test_date=test_date).all()
        reactions_visual_errors = reactions_results[0].visual_errors if reactions_results else None
        reactions_audio_errors = reactions_results[0].audio_errors if reactions_results else None
        reactions_visual_errors_average = db.query(func.avg(models.ReactionsTestResult.visual_errors)).filter_by(user_id=user.id).scalar()
        reactions_audio_errors_average = db.query(func.avg(models.ReactionsTestResult.audio_errors)).filter_by(user_id=user.id).scalar()

        text_audition_results = db.query(models.TextAuditionResults).filter_by(user_id=user.id, test_date=test_date).all()
        pauses_count_read = text_audition_results[0].pauses_count_read if text_audition_results else None
        pauses_count_repeat = text_audition_results[0].pauses_count_repeat if text_audition_results else None
        pauses_count_read_average = db.query(func.avg(models.TextAuditionResults.pauses_count_read)).filter_by(user_id=user.id).scalar()
        pauses_count_repeat_average = db.query(func.avg(models.TextAuditionResults.pauses_count_repeat)).filter_by(user_id=user.id).scalar()
        average_volume_read = text_audition_results[0].average_volume_read if text_audition_results else None
        average_volume_repeat = text_audition_results[0].average_volume_repeat if text_audition_results else None
        average_volume_read_average = db.query(func.avg(models.TextAuditionResults.average_volume_read)).filter_by(user_id=user.id).scalar()
        average_volume_repeat_average = db.query(func.avg(models.TextAuditionResults.average_volume_repeat)).filter_by(user_id=user.id).scalar()

        # Вызов твоей функции
        fs_score = calculate_fs_score(
            shtange_result_indicator=shtange_result_indicator,
            shtange_test_result_indicator_average=shtange_test_result_indicator_average,
            personal_report=personal_report_indicator,
            personal_report_average=personal_report_indicator_average,
            pulseAverage=pulseAverage,
            pulseAverageAllDays=pulse_alltime_average,
            rufie_result_indicator=rufie_result_indicator,
            strup_result=strup_result,
            strup_test_result_average=strup_test_result_average,
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
            average_volume_repeat_average=average_volume_repeat_average
        )
        fs_score_list.append(DailyEstimationResult(
            date=str(test_date),
            estimation=fs_score,
        ))

    return fs_score_list

@router.get("/last-gench-result", response_model=LastGenchResult)
def get_last_gench_result(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    # Все тесты пользователя (по дате по возрастанию)
    gench_qs = (
        db.query(models.GenchTestResult)
        .filter(models.GenchTestResult.user_id == user.id)
        .order_by(models.GenchTestResult.test_date.asc(), models.GenchTestResult.created_at.asc())
        .all()
    )

    if not gench_qs:
        # Нет ни одного теста — возвращаем "пустой" объект
        return LastGenchResult(
            heartRateBefore=None,
            heartRateAfter=None,
            genchIndicator=None,
            genchIndicatorAvg=None,
            genchIndicators=[],
            estimate=None,
            estimates=[],
        )

    last_obj = gench_qs[-1]

    # Список индикаторов и среднее
    indicators = [
        obj.reaction_indicator
        for obj in gench_qs
        if obj.reaction_indicator is not None
    ]
    gench_indicator_avg = (
        sum(indicators) / len(indicators) if indicators else None
    )

    # Список всех индикаторов по датам
    gench_indicators = [
        GenchDailyResults(
            indicator=obj.reaction_indicator,
            date=str(obj.test_date),
        )
        for obj in gench_qs
        if obj.reaction_indicator is not None
    ]

    # Все текстовые оценки
    estimates = [
        obj.result_estimation
        for obj in gench_qs
        if obj.result_estimation is not None
    ]

    return LastGenchResult(
        heartRateBefore=last_obj.heart_rate_before,
        heartRateAfter=last_obj.heart_rate_after,
        genchIndicator=last_obj.reaction_indicator,
        genchIndicatorAvg=gench_indicator_avg,
        genchIndicators=gench_indicators,
        estimate=last_obj.result_estimation,
        estimates=estimates,
    )

@router.get("/last-shtange-result", response_model=LastShtangeResult)
def get_last_shtange_result(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    shtange_qs = (
        db.query(models.ShtangeTestResult)
        .filter(models.ShtangeTestResult.user_id == user.id)
        .order_by(models.ShtangeTestResult.test_date.asc(), models.ShtangeTestResult.created_at.asc())
        .all()
    )

    if not shtange_qs:
        return LastShtangeResult(
            heartRateBefore=None,
            heartRateAfter=None,
            shtangeIndicator=None,
            shtangeIndicatorAvg=None,
            shtangeIndicators=[],
            estimate=None,
            estimates=[],
        )

    last_obj = shtange_qs[-1]

    indicators = [
        obj.reaction_indicator
        for obj in shtange_qs
        if obj.reaction_indicator is not None
    ]
    shtange_indicator_avg = (
        sum(indicators) / len(indicators) if indicators else None
    )

    shtange_indicators = [
        ShtangeDailyResults(
            indicator=obj.reaction_indicator,
            date=str(obj.test_date),
        )
        for obj in shtange_qs
        if obj.reaction_indicator is not None
    ]

    estimates = [
        obj.result_estimation
        for obj in shtange_qs
        if obj.result_estimation is not None
    ]

    return LastShtangeResult(
        heartRateBefore=last_obj.heart_rate_before,
        heartRateAfter=last_obj.heart_rate_after,
        shtangeIndicator=last_obj.reaction_indicator,
        shtangeIndicatorAvg=shtange_indicator_avg,
        shtangeIndicators=shtange_indicators,
        estimate=last_obj.result_estimation,
        estimates=estimates,
    )

@router.get("/last-reactions-result", response_model=LastReactionsResult)
def get_last_reactions_result(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    reactions_qs = (
        db.query(models.ReactionsTestResult)
        .filter(models.ReactionsTestResult.user_id == user.id)
        .order_by(models.ReactionsTestResult.test_date.asc(), models.ReactionsTestResult.created_at.asc())
        .all()
    )

    if not reactions_qs:
        return LastReactionsResult(
            audioResultMistakes=None,
            videoResultMistakes=None,
            reactionResultAudioAvgResult=None,
            reactionResultAudioAvgAlltimeResult=None,
            reactionResultAudioStdResult=None,
            reactionResultVisualAvgResult=None,
            reactionResultVisualAvgAlltimeResult=None,
            reactionResultVisualStdResult=None,
            reactionsAudio=[],
            reactionsVisual=[],
        )

    last_obj = reactions_qs[-1]

    # Средние по всем тестам
    audio_avgs = [
        obj.audio_average_diff
        for obj in reactions_qs
        if obj.audio_average_diff is not None
    ]
    visual_avgs = [
        obj.visual_average_diff
        for obj in reactions_qs
        if obj.visual_average_diff is not None
    ]

    audio_avg_alltime = (
        sum(audio_avgs) / len(audio_avgs) if audio_avgs else None
    )
    visual_avg_alltime = (
        sum(visual_avgs) / len(visual_avgs) if visual_avgs else None
    )

    # Списки по дням
    reactions_audio = [
        ReactionsAvgDailyResult(
            indicator=obj.audio_average_diff,
            date=str(obj.test_date),
        )
        for obj in reactions_qs
        if obj.audio_average_diff is not None
    ]

    reactions_visual = [
        ReactionsAvgDailyResult(
            indicator=obj.visual_average_diff,
            date=str(obj.test_date),
        )
        for obj in reactions_qs
        if obj.visual_average_diff is not None
    ]

    return LastReactionsResult(
        audioResultMistakes=last_obj.audio_errors,
        videoResultMistakes=last_obj.visual_errors,

        reactionResultAudioAvgResult=last_obj.audio_average_diff,
        reactionResultAudioAvgAlltimeResult=audio_avg_alltime,
        reactionResultAudioStdResult=last_obj.audio_quav_diff,

        reactionResultVisualAvgResult=last_obj.visual_average_diff,
        reactionResultVisualAvgAlltimeResult=visual_avg_alltime,
        reactionResultVisualStdResult=last_obj.visual_quav_diff,

        reactionsAudio=reactions_audio,
        reactionsVisual=reactions_visual,
    )