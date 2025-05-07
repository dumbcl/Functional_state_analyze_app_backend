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

    def format_line(name, value):
        return f"{name}: {value}" if value is not None else None

    lines = [
        format_line("Проба Штанге (индекс)", shtange_result_indicator),
        format_line("Средний показатель пробы Штанге", shtange_test_result_indicator_average),
        format_line("Самооценка состояния", personal_report),
        format_line("Средняя самооценка состояния", personal_report_average),
        format_line("Средний пульс за день", pulseAverage),
        format_line("Средний пульс за все дни", pulseAverageAllDays),
        format_line("Показатель Руфье", rufie_result_indicator),
        format_line("Результат теста Струпа", strup_result),
        format_line("Средний результат теста Струпа", strup_test_result_average),
        format_line("Проба Генча (индекс)", gench_result_indicator),
        format_line("Средний показатель пробы Генча", gench_test_result_indicator_average),
        format_line("Ошибки реакции на свет", reactions_visual_errors),
        format_line("Ошибки реакции на звук", reactions_audio_errors),
        format_line("Среднее ошибок реакции на свет", reactions_visual_errors_average),
        format_line("Среднее ошибок реакции на звук", reactions_audio_errors_average),
        format_line("Количество пауз при чтении", pauses_count_read),
        format_line("Количество пауз при повторении", pauses_count_repeat),
        format_line("Среднее количество пауз при чтении", pauses_count_read_average),
        format_line("Среднее количество пауз при повторении", pauses_count_repeat_average),
        format_line("Средняя громкость при чтении", average_volume_read),
        format_line("Средняя громкость при повторении", average_volume_repeat),
        format_line("Среднее громкости при чтении за предыдущие дни", average_volume_read_average),
        format_line("Среднее громкости при повторении за предыдущие дни", average_volume_repeat_average)
    ]

    prompt = "Вот список показателей функционального состояния пользователя:\n\n" + \
             "\n".join([line for line in lines if line]) + "\n\n"

    if fs_category is not None:
        prompt += f"С помощью своей функции я оценил эти показатели как: {fs_category}.\n\n"

    prompt += "Напиши короткое описание для пользователя, поясняющее его сегодняшнее функциональное состояние, возможные причины такого результата и рекомендации по улучшению состояния."

    messages = [
        {"role": "system", "text": "Ты помощник, который анализирует показатели функционального состояния и дает краткое понятное описание и рекомендации."},
        {"role": "user", "text": prompt}
    ]

    result = sdk.models.completions("yandexgpt").configure(temperature=0.5).run(messages)

    description = next(iter(result)).text

    return description
