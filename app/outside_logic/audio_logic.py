import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.metrics import edit_distance
import re
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import json
from argparse import ArgumentParser
from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType
import os

def recognize(audio):
   configure_credentials(
       yandex_credentials=creds.YandexCredentials(api_key=os.getenv("YANDEX_API_KEY"))
   )
   model = model_repository.recognition_model()

   # Specify the recognition settings.
   model.model = 'general'
   model.language = 'ru-RU'
   model.audio_processing_type = AudioProcessingType.Full

   # Recognizing speech in the specified audio file and outputting the results to the console.
   result = model.transcribe_file(audio)
   raw_text = ""
   for c, res in enumerate(result):
      raw_text += res.raw_text
   return raw_text

class TextComparer:
    def __init__(self, language='russian'):
        """
        Инициализация анализатора соответствия текстов

        :param language: язык текста ('russian', 'english' и др.)
        """
        for res in ("punkt", "stopwords"):
            try:
                nltk.data.find(res)
            except LookupError:
                nltk.download(res, quiet=True)
        self.language = language
        self.stops = set(stopwords.words(language)) if language in stopwords.fileids else set()

    def preprocess_text(self, text, remove_stopwords=False):
        """
        Предобработка текста: приведение к нижнему регистру,
        удаление знаков пунктуации и стоп-слов (опционально)

        :param text: текст для обработки
        :param remove_stopwords: удалять ли стоп-слова
        :return: обработанный список слов
        """
        # Приведение к нижнему регистру
        text = text.lower()

        # Удаление знаков пунктуации и цифр
        text = re.sub(r'[^\w\s]|[\d]', ' ', text)

        # Токенизация
        tokens = word_tokenize(text)

        # Удаление стоп-слов (если требуется)
        if remove_stopwords:
            tokens = [word for word in tokens if word not in self.stops]

        return tokens

    def word_error_rate(self, reference, hypothesis):
        """
        Расчет Word Error Rate (WER)

        :param reference: эталонный текст (список слов)
        :param hypothesis: проверяемый текст (список слов)
        :return: WER, количество замен, вставок, удалений
        """
        # Используем расстояние Левенштейна для последовательностей
        edit_matrix = np.zeros((len(reference) + 1, len(hypothesis) + 1))

        # Заполнение первого столбца и строки
        for i in range(len(reference) + 1):
            edit_matrix[i][0] = i
        for j in range(len(hypothesis) + 1):
            edit_matrix[0][j] = j

        # Заполнение матрицы
        for i in range(1, len(reference) + 1):
            for j in range(1, len(hypothesis) + 1):
                if reference[i - 1] == hypothesis[j - 1]:
                    edit_matrix[i][j] = edit_matrix[i - 1][j - 1]
                else:
                    substitution = edit_matrix[i - 1][j - 1] + 1
                    insertion = edit_matrix[i][j - 1] + 1
                    deletion = edit_matrix[i - 1][j] + 1
                    edit_matrix[i][j] = min(substitution, insertion, deletion)

        # Подсчет операций редактирования
        i, j = len(reference), len(hypothesis)
        substitutions, insertions, deletions = 0, 0, 0

        while i > 0 or j > 0:
            if i > 0 and j > 0 and reference[i - 1] == hypothesis[j - 1]:
                i, j = i - 1, j - 1
            else:
                if i > 0 and j > 0 and edit_matrix[i][j] == edit_matrix[i - 1][j - 1] + 1:
                    substitutions += 1
                    i, j = i - 1, j - 1
                elif j > 0 and edit_matrix[i][j] == edit_matrix[i][j - 1] + 1:
                    insertions += 1
                    j = j - 1
                elif i > 0 and edit_matrix[i][j] == edit_matrix[i - 1][j] + 1:
                    deletions += 1
                    i = i - 1

        wer = (substitutions + insertions + deletions) / max(len(reference), 1)
        return wer, substitutions, insertions, deletions

    def cosine_sim(self, reference, hypothesis):
        """
        Расчет косинусного сходства между текстами

        :param reference: эталонный текст
        :param hypothesis: проверяемый текст
        :return: косинусное сходство (0-1)
        """
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([reference, hypothesis])
        return cosine_similarity(vectors)[0, 1]

    def jaccard_similarity(self, set1, set2):
        """
        Расчет сходства Жаккара между множествами слов

        :param set1: первое множество слов
        :param set2: второе множество слов
        :return: коэффициент Жаккара (0-1)
        """
        set1, set2 = set(set1), set(set2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / max(union, 1)

    def highlight_differences(self, reference, hypothesis):
        """
        Подсветка различий между текстами

        :param reference: эталонный текст
        :param hypothesis: проверяемый текст
        :return: словарь с подсвеченными различиями
        """
        # Используем difflib для нахождения различий
        d = difflib.Differ()
        diff = list(d.compare(reference.split(), hypothesis.split()))

        # Классификация различий
        reference_only = [word[2:] for word in diff if word.startswith('- ')]
        hypothesis_only = [word[2:] for word in diff if word.startswith('+ ')]
        common = [word[2:] for word in diff if word.startswith('  ')]

        return {
            'common_words': common,
            'missing_in_hypothesis': reference_only,
            'extra_in_hypothesis': hypothesis_only
        }

    def analyze(self, reference_text, hypothesis_text, detailed=True):
        """
        Полный анализ соответствия текстов

        :param reference_text: эталонный текст
        :param hypothesis_text: проверяемый текст (распознанный из речи)
        :param detailed: включить подробный анализ
        :return: словарь с результатами анализа
        """
        # Предобработка текстов
        reference_raw = reference_text.strip()
        hypothesis_raw = hypothesis_text.strip()

        reference_tokens = self.preprocess_text(reference_raw)
        hypothesis_tokens = self.preprocess_text(hypothesis_raw)

        # Основные метрики
        wer, substitutions, insertions, deletions = self.word_error_rate(reference_tokens, hypothesis_tokens)
        cosine = self.cosine_sim(reference_raw, hypothesis_raw)
        jaccard = self.jaccard_similarity(reference_tokens, hypothesis_tokens)

        # Точность на уровне слов (сколько правильных слов из всех)
        correct_words = len(reference_tokens) - (substitutions + deletions)
        word_accuracy = correct_words / max(len(reference_tokens), 1)

        # Процент распознанного текста
        recognition_completeness = 1 - (deletions / max(len(reference_tokens), 1))

        # Результаты анализа
        result = {
            'word_error_rate': wer,
            'word_accuracy': word_accuracy,
            'cosine_similarity': cosine,
            'jaccard_similarity': jaccard,
            'recognition_completeness': recognition_completeness,
            'error_details': {
                'substitutions': substitutions,
                'insertions': insertions,
                'deletions': deletions
            },
            'reference_word_count': len(reference_tokens),
            'transcript_word_count': len(hypothesis_tokens)
        }

        # Дополнительный детальный анализ
        if detailed:
            diff_details = self.highlight_differences(reference_raw, hypothesis_raw)
            result['differences'] = diff_details

            # Оценка по шкале от 0 до 100
            accuracy_score = min(100, max(0, 100 * (1 - wer)))
            similarity_score = min(100, max(0, 100 * (0.6 * cosine + 0.4 * jaccard)))

            # Обобщенная оценка качества повторения
            overall_score = min(100, max(0, (0.7 * accuracy_score + 0.3 * similarity_score)))

            result['scores'] = {
                'accuracy_score': round(accuracy_score, 1),
                'similarity_score': round(similarity_score, 1),
                'overall_score': round(overall_score, 1)
            }

            # Качественная оценка
            if overall_score >= 90:
                quality = "Отлично"
            elif overall_score >= 75:
                quality = "Хорошо"
            elif overall_score >= 60:
                quality = "Удовлетворительно"
            else:
                quality = "Требуется улучшение"

            result['quality_assessment'] = quality

        return result


def analyze_audio_volume_and_pauses(file_path, pause_threshold_db=20, min_pause_duration=1.5):
    y, sr = librosa.load(file_path)

    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

    mean_volume = np.mean(rms)

    # Переводим RMS в дБ для лучшей работы с порогами
    db_rms = librosa.amplitude_to_db(rms, ref=np.max)

    # Сглаживаем кривую громкости медианным фильтром
    db_rms_smooth = medfilt(db_rms, kernel_size=15)

    # Вычисляем адаптивный порог на основе локального среднего
    window_size = int(sr / hop_length * 3)  # окно в 3 секунды
    local_mean = np.zeros_like(db_rms_smooth)

    for i in range(len(db_rms_smooth)):
        start = max(0, i - window_size // 2)
        end = min(len(db_rms_smooth), i + window_size // 2)
        local_mean[i] = np.mean(db_rms_smooth[start:end])

    threshold = local_mean - pause_threshold_db
    is_pause = db_rms_smooth < threshold

    min_pause_frames = int(min_pause_duration * sr / hop_length)

    pauses = []
    current_pause_start = None

    for i in range(len(is_pause)):
        if is_pause[i] and (i == 0 or not is_pause[i - 1]):
            current_pause_start = i
        elif not is_pause[i] and i > 0 and is_pause[i - 1] and current_pause_start is not None:
            if i - current_pause_start >= min_pause_frames:
                start_time = current_pause_start * hop_length / sr
                end_time = i * hop_length / sr
                duration = end_time - start_time
                pauses.append((start_time, end_time, duration))
            current_pause_start = None

    if current_pause_start is not None and len(is_pause) - current_pause_start >= min_pause_frames:
        start_time = current_pause_start * hop_length / sr
        end_time = len(is_pause) * hop_length / sr
        duration = end_time - start_time
        pauses.append((start_time, end_time, duration))

    return mean_volume, len(pauses)