import yandex_cloud_ml_sdk
import os

def generate_fs_description(
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
    average_volume_repeat_average,
    fs_category,
    fs_score
) -> str:

    folder_id = os.getenv("YANDEX_FOLDER_ID")
    if not folder_id:
        return ""

    api_key = os.getenv("YANDEX_API_KEY")
    if not api_key:
        return ""

    sdk = yandex_cloud_ml_sdk.YCloudML(
        folder_id=folder_id,
        auth=api_key,
    )

    prompt = f"""Вот список показателей функционального состояния пользователя:

Проба Штанге (индекс): {shtange_result_indicator}
Средний показатель пробы Штанге: {shtange_test_result_indicator_average}
Самооценка состояния: {personal_report}
Средняя самооценка состояния: {personal_report_average}
Средний пульс за день: {pulseAverage}
Средний пульс за все дни: {pulseAverageAllDays}
Показатель Руфье: {rufie_result_indicator}
Результат теста Струпа: {strup_result}
Средний результат теста Струпа: {strup_test_result_average}
Проба Генча (индекс): {gench_result_indicator}
Средний показатель пробы Генча: {gench_test_result_indicator_average}
Ошибки реакции на свет: {reactions_visual_errors}
Ошибки реакции на звук: {reactions_audio_errors}
Среднее ошибок реакции на свет: {reactions_visual_errors_average}
Среднее ошибок реакции на звук: {reactions_audio_errors_average}
Количество пауз при чтении: {pauses_count_read}
Количество пауз при повторении: {pauses_count_repeat}
Среднее количество пауз при чтении: {pauses_count_read_average}
Среднее количество пауз при повторении: {pauses_count_repeat_average}
Средняя громкость при чтении: {average_volume_read}
Средняя громкость при повторении: {average_volume_repeat}
Среднее громкости при чтении за предыдущие дни: {average_volume_read_average}
Среднее громкости при повторении за предыдущие дни: {average_volume_repeat_average}

С помощью своей функции я оценил эти показатели как: {fs_category}.

Напиши короткое описание для пользователя, поясняющее его сегодняшнее функциональное состояние, возможные причины такого результата и рекомендации по улучшению состояния."""

    messages = [
        {"role": "system", "text": "Ты помощник, который анализирует показатели функционального состояния и дает краткое понятное описание и рекомендации."},
        {"role": "user", "text": prompt}
    ]

    result = sdk.models.completions("yandexgpt").configure(temperature=0.5).run(messages)

    description = next(iter(result)).text

    return description
