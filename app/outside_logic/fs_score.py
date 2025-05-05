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
    if shtange_result_indicator > 1.2 or shtange_result_indicator > shtange_test_result_indicator_average:
        score -= 2

    if personal_report < 30:
        score -= 2
    elif personal_report > 70:
        score += 2

    if rufie_result_indicator > 15:
        score -= 2
    elif rufie_result_indicator < 5:
        score += 2

    if strup_result < 30:
        score -= 2
    elif strup_result > 60:
        score += 2

    if gench_result_indicator > 1.2 or gench_result_indicator > gench_test_result_indicator_average:
        score -= 2

    # Дополнительные показатели
    if personal_report < personal_report_average * 0.85:
        score -= 1

    pulse_diff = abs(pulseAverage - pulseAverageAllDays) / pulseAverageAllDays
    if pulse_diff > 0.2:
        score -= 1

    if strup_result < strup_test_result_average * 0.85:
        score -= 1

    if reactions_visual_errors > reactions_visual_errors_average * 1.15:
        score -= 1

    if reactions_audio_errors > reactions_audio_errors_average * 1.15:
        score -= 1

    if pauses_count_read > pauses_count_read_average * 1.15:
        score -= 1

    if pauses_count_repeat > pauses_count_repeat_average * 1.15:
        score -= 1

    vol_read_diff = abs(average_volume_read - average_volume_read_average) / average_volume_read_average
    if vol_read_diff > 0.15:
        score -= 1

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

def evaluate_shtange(shtange_result_indicator, shtange_average):
    if shtange_result_indicator > 1.2 or shtange_result_indicator > shtange_average * 1.15:
        return 'BAD'
    return 'GOOD'

def evaluate_personal_report(personal_report):
    if personal_report < 30:
        return 'BAD'
    elif personal_report > 70:
        return 'GOOD'
    return 'MEDIUM'

def evaluate_rufie(rufie_result_indicator):
    if rufie_result_indicator > 15:
        return 'BAD'
    elif rufie_result_indicator < 5:
        return 'GOOD'
    return 'MEDIUM'

def evaluate_strup(strup_result):
    if strup_result < 30:
        return 'BAD'
    elif strup_result > 60:
        return 'GOOD'
    return 'MEDIUM'

def evaluate_gench(gench_result_indicator, gench_average):
    if gench_result_indicator > 1.2 or gench_result_indicator > gench_average * 1.15:
        return 'BAD'
    return 'GOOD'

def evaluate_reactions_visual_errors(errors, average):
    if errors > average * 1.15:
        return 'BAD'
    return 'GOOD'

def evaluate_reactions_audio_errors(errors, average):
    if errors > average * 1.15:
        return 'BAD'
    return 'GOOD'

def evaluate_pauses_count_read(pauses, average):
    if pauses > average * 1.15:
        return 'BAD'
    return 'GOOD'

def evaluate_pauses_count_repeat(pauses, average):
    if pauses > average * 1.15:
        return 'BAD'
    return 'GOOD'

def evaluate_pulse(pulse_daily_average, pulse_alltime_average):
    if pulse_daily_average > 1.2 * pulse_alltime_average or pulse_daily_average * 1.2 < pulse_alltime_average:
        return 'BAD'
    return 'GOOD'
