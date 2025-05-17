from typing import Optional

from app.schemas import ShtangeTestResult, PersonalReportTestResult, PulseMeasurementResult, RufieTestResult, \
    StrupTestResult, GenchTestResult, ReactionsTestResult, TextAuditionTestResult, EscalDailyTestResult


def calculate_fs_category(
    shtange_result_indicator,
    shtange_test_result_indicator_average,
    personal_report,
    personal_report_average,
    pulseAverage,
    pulseAverageAllDays,
    rufie_result_indicator,
    strup_result,
    strup_test_result_average,
    gench_result_indicator,
    gench_test_result_indicator_average,
    reactions_visual_errors,
    reactions_audio_errors,
    reactions_visual_errors_average,
    reactions_audio_errors_average,
    pauses_count_read,
    pauses_count_repeat,
    pauses_count_read_average,
    pauses_count_repeat_average,
    average_volume_read,
    average_volume_repeat,
    average_volume_read_average,
    average_volume_repeat_average
) -> str:

    score = 10

    # Объективные показатели
    if (shtange_result_indicator is not None) and (shtange_test_result_indicator_average is not None):
        if shtange_result_indicator > 1.2 or shtange_result_indicator > shtange_test_result_indicator_average:
            score -= 2

    if personal_report is not None:
        if personal_report < 30:
            score -= 2
        elif personal_report > 70:
            score += 2

    if rufie_result_indicator is not None:
        if rufie_result_indicator > 15:
            score -= 2
        elif rufie_result_indicator < 5:
            score += 2

    if strup_result is not None:
        if strup_result < 10:
            score -= 2
        elif strup_result > 17:
            score += 2

    if (gench_result_indicator is not None) and (gench_test_result_indicator_average is not None):
        if gench_result_indicator > 1.2 or gench_result_indicator > gench_test_result_indicator_average:
            score -= 2

    # Дополнительные показатели
    if (personal_report is not None) and (personal_report_average is not None):
        if float(personal_report) < personal_report_average * 0.85:
            score -= 1

    if (pulseAverage is not None) and (pulseAverageAllDays is not None) and (pulseAverageAllDays != 0):
        pulse_diff = abs(pulseAverage - pulseAverageAllDays) / pulseAverageAllDays
        if pulse_diff > 0.2:
            score -= 1

    if (strup_result is not None) and (strup_test_result_average is not None):
        if float(strup_result) < float(strup_test_result_average) * 0.85:
            score -= 1

    if (reactions_visual_errors is not None) and (reactions_visual_errors_average is not None):
        if float(reactions_visual_errors) > float(reactions_visual_errors_average) * 1.15:
            score -= 1

    if (reactions_audio_errors is not None) and (reactions_audio_errors_average is not None):
        if float(reactions_audio_errors) > float(reactions_audio_errors_average) * 1.15:
            score -= 1

    if (pauses_count_read is not None) and (pauses_count_read_average is not None):
        if float(pauses_count_read) > float(pauses_count_read_average) * 1.15:
            score -= 1

    if (pauses_count_repeat is not None) and (pauses_count_repeat_average is not None):
        if float(pauses_count_repeat) > float(pauses_count_repeat_average) * 1.15:
            score -= 1

    if (average_volume_read is not None) and (average_volume_read_average is not None) and (average_volume_read_average != 0):
        vol_read_diff = abs(average_volume_read - average_volume_read_average) / average_volume_read_average
        if vol_read_diff > 0.15:
            score -= 1

    if (average_volume_repeat is not None) and (average_volume_repeat_average is not None) and (average_volume_repeat_average != 0):
        vol_repeat_diff = abs(average_volume_repeat - average_volume_repeat_average) / average_volume_repeat_average
        if vol_repeat_diff > 0.15:
            score -= 1

    # Определение категории
    if score >= 11:
        category = 'GOOD'
    elif 7 <= score <= 10:
        category = 'MEDIUM'
    else:
        category = 'BAD'

    return category

# Отдельные функции для оценки каждого показателя

def evaluate_shtange(shtange_result, shtange_result_indicator, shtange_average, date) -> Optional[ShtangeTestResult]:
    if None in (shtange_result, shtange_result_indicator, shtange_average):
        return None
    status = 'BAD' if shtange_result_indicator > 1.2 or shtange_result_indicator > shtange_average * 1.15 else 'GOOD'
    return ShtangeTestResult(
        shtange_result=shtange_result,
        shtange_result_indicator=shtange_result_indicator,
        shtange_test_result_indicator_average=shtange_average,
        type=status,
        date=date,
    )

def evaluate_personal_report(report_text, report_current, report_average, date) -> Optional[PersonalReportTestResult]:
    if None in (report_text, report_current, report_average):
        return None
    if report_current < 30:
        status = 'BAD'
    elif report_current > 70:
        status = 'GOOD'
    else:
        status = 'MEDIUM'
    return PersonalReportTestResult(
        personal_report_about_day=report_text,
        personal_report_current=report_current,
        personal_report_current_average=report_average,
        type=status,
        date=date,
    )

def evaluate_pulse(pulse_avg, pulse_max, pulse_min, pulse_alltime_avg, date) -> Optional[PulseMeasurementResult]:
    if (None in (pulse_avg, pulse_max, pulse_min, pulse_alltime_avg)) and (pulse_alltime_avg != 0):
        return None
    deviation = abs(pulse_avg - pulse_alltime_avg) / pulse_alltime_avg
    status = 'BAD' if deviation > 0.2 else 'GOOD'
    return PulseMeasurementResult(
        pulseAverage=pulse_avg,
        pulseMax=pulse_max,
        pulseMin=pulse_min,
        type=status,
        date=date,
    )

def evaluate_rufie(rufie_result, rufie_indicator, rufie_avg, date) -> Optional[RufieTestResult]:
    if None in (rufie_result, rufie_indicator, rufie_avg):
        return None
    if rufie_indicator > 15:
        status = 'BAD'
    elif rufie_indicator < 5:
        status = 'GOOD'
    else:
        status = 'MEDIUM'
    return RufieTestResult(
        rufie_result=rufie_result,
        rufie_result_indicator=rufie_indicator,
        rufie_test_result_indicator_average=rufie_avg,
        type=status,
        date=date,
    )

def evaluate_strup(strup_result_estimation, strup_result, strup_avg, date) -> Optional[StrupTestResult]:
    if None in (strup_result_estimation, strup_result, strup_avg):
        return None
    if strup_result < 10:
        status = 'BAD'
    elif strup_result > 17:
        status = 'GOOD'
    else:
        status = 'MEDIUM'
    return StrupTestResult(
        strup_result_estimation=strup_result_estimation,
        strup_result=strup_result,
        strup_test_result_average=strup_avg,
        type=status,
        date=date,
    )

def evaluate_gench(gench_result_estimation, gench_indicator, gench_avg, date) -> Optional[GenchTestResult]:
    if None in (gench_result_estimation, gench_indicator, gench_avg):
        return None
    status = 'BAD' if gench_indicator > 1.2 or gench_indicator > gench_avg * 1.15 else 'GOOD'
    return GenchTestResult(
        gench_result_estimation=gench_result_estimation,
        gench_result_indicator=gench_indicator,
        gench_test_result_indicator_average=gench_avg,
        type=status,
        date=date,
    )

def evaluate_reactions(visual, audio, visual_avg, audio_avg,
    reactions_visual_diff_avg,reactions_audio_diff_avg, reactions_audio_std_avg,
                       reactions_visual_std_avg, date) -> Optional[ReactionsTestResult]:
    if None in (visual, audio, visual_avg, audio_avg):
        return None
    visual_status = 'BAD' if float(visual) > float(visual_avg) * 1.15 else 'GOOD'
    audio_status = 'BAD' if float(audio) > float(audio_avg) * 1.15 else 'GOOD'
    return ReactionsTestResult(
        reactions_visual_errors=visual,
        reactions_audio_errors=audio,
        reactions_visual_errors_average=visual_avg,
        reactions_audio_errors_average=audio_avg,
        reactions_visual_errors_type=visual_status,
        reactions_audio_errors_type=audio_status,
        reactions_visual_diff_avg=reactions_visual_diff_avg,
        reactions_audio_diff_avg=reactions_audio_diff_avg,
        reactions_audio_std_avg=reactions_audio_std_avg,
        reactions_visual_std_avg=reactions_visual_std_avg,
        date=date
    )

def evaluate_text_audition(pauses_read, pauses_repeat, pauses_read_avg, pauses_repeat_avg,
                            vol_read, vol_repeat, vol_read_avg, vol_repeat_avg, quality_score_read, quality_score_read_avg,
                           quality_score_repeat, quality_score_repeat_avg, date) -> Optional[TextAuditionTestResult]:
    if None in (pauses_read, pauses_repeat, pauses_read_avg, pauses_repeat_avg,
                vol_read, vol_repeat, vol_read_avg, vol_repeat_avg, quality_score_repeat, quality_score_repeat_avg):
        return None
    quality_read_status = 'BAD' if quality_score_read < quality_score_read_avg * 1.15 else 'GOOD'
    quality_repeat_status = 'BAD' if float(quality_score_repeat) < float(quality_score_repeat_avg) * 1.15 else 'GOOD'
    return TextAuditionTestResult(
        pauses_count_read=pauses_read,
        pauses_count_repeat=pauses_repeat,
        pauses_count_read_average=pauses_read_avg,
        pauses_count_repeat_average=pauses_repeat_avg,
        average_volume_read=vol_read,
        average_volume_repeat=vol_repeat,
        average_volume_read_average=vol_read_avg,
        average_volume_repeat_average=vol_repeat_avg,
        quality_read=quality_score_read,
        quality_repeat=quality_score_repeat,
        quality_read_average=quality_score_read_avg,
        quality_repeat_average=quality_score_repeat_avg,
        quality_read_type=quality_read_status,
        quality_repeat_type=quality_repeat_status,
        date=date
    )

def evaluate_escal_daily(performance, fatigue, anxiety, conflict, sanX, sanZ, date) -> Optional[EscalDailyTestResult]:
    if None in (performance, fatigue, anxiety, conflict, sanX, sanZ):
        return None

    performance_status = "GOOD" if performance > 7 else "BAD" if performance < 4 else "MEDIUM"
    fatigue_status = "BAD" if fatigue > 7 else "GOOD" if fatigue < 4 else "MEDIUM"
    anxiety_status = "BAD" if anxiety > 7 else "GOOD" if anxiety < 4 else "MEDIUM"
    conflict_status = "BAD" if conflict > 7 else "GOOD" if conflict < 4 else "MEDIUM"

    return EscalDailyTestResult(
        performance=performance,
        performance_type=performance_status,
        fatigue=fatigue,
        fatigue_type=fatigue_status,
        anxiety=anxiety,
        anxiety_type=anxiety_status,
        conflict=conflict,
        conflict_type=conflict_status,
        sanX=sanX,
        sanZ=sanZ,
        date=date,
    )


def calculate_fs_score(
    shtange_result_indicator,
    shtange_test_result_indicator_average,
    personal_report,
    personal_report_average,
    pulseAverage,
    pulseAverageAllDays,
    rufie_result_indicator,
    strup_result,
    strup_test_result_average,
    gench_result_indicator,
    gench_test_result_indicator_average,
    reactions_visual_errors,
    reactions_audio_errors,
    reactions_visual_errors_average,
    reactions_audio_errors_average,
    pauses_count_read,
    pauses_count_repeat,
    pauses_count_read_average,
    pauses_count_repeat_average,
    average_volume_read,
    average_volume_repeat,
    average_volume_read_average,
    average_volume_repeat_average
) -> int:

    score = 10

    # Объективные показатели
    if (shtange_result_indicator is not None) and (shtange_test_result_indicator_average is not None):
        if shtange_result_indicator > 1.2 or shtange_result_indicator > shtange_test_result_indicator_average:
            score -= 2

    if personal_report is not None:
        if personal_report < 30:
            score -= 2
        elif personal_report > 70:
            score += 2

    if rufie_result_indicator is not None:
        if rufie_result_indicator > 15:
            score -= 2
        elif rufie_result_indicator < 5:
            score += 2

    if strup_result is not None:
        if strup_result < 10:
            score -= 2
        elif strup_result > 17:
            score += 2

    if (gench_result_indicator is not None) and (gench_test_result_indicator_average is not None):
        if gench_result_indicator > 1.2 or gench_result_indicator > gench_test_result_indicator_average:
            score -= 2

    # Дополнительные показатели
    if (personal_report is not None) and (personal_report_average is not None):
        if float(personal_report) < personal_report_average * 0.85:
            score -= 1

    if (pulseAverage is not None) and (pulseAverageAllDays is not None) and (pulseAverageAllDays != 0):
        pulse_diff = abs(pulseAverage - pulseAverageAllDays) / pulseAverageAllDays
        if pulse_diff > 0.2:
            score -= 1

    if (strup_result is not None) and (strup_test_result_average is not None):
        if float(strup_result) < float(strup_test_result_average) * 0.85:
            score -= 1

    if (reactions_visual_errors is not None) and (reactions_visual_errors_average is not None):
        if float(reactions_visual_errors) > float(reactions_visual_errors_average) * 1.15:
            score -= 1

    if (reactions_audio_errors is not None) and (reactions_audio_errors_average is not None):
        if float(reactions_audio_errors) > float(reactions_audio_errors_average) * 1.15:
            score -= 1

    if (pauses_count_read is not None) and (pauses_count_read_average is not None):
        if float(pauses_count_read) > float(pauses_count_read_average) * 1.15:
            score -= 1

    if (pauses_count_repeat is not None) and (pauses_count_repeat_average is not None):
        if float(pauses_count_repeat) > float(pauses_count_repeat_average) * 1.15:
            score -= 1

    if (average_volume_read is not None) and (average_volume_read_average is not None) and (average_volume_read_average != 0):
        vol_read_diff = abs(average_volume_read - average_volume_read_average) / average_volume_read_average
        if vol_read_diff > 0.15:
            score -= 1

    if (average_volume_repeat is not None) and (average_volume_repeat_average is not None) and (average_volume_repeat_average != 0):
        vol_repeat_diff = abs(average_volume_repeat - average_volume_repeat_average) / average_volume_repeat_average
        if vol_repeat_diff > 0.15:
            score -= 1

    return score

