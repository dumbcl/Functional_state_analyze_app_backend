from __future__ import annotations

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
import difflib
import json
from argparse import ArgumentParser
from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType
import os
import difflib
import re
from typing import Dict, List, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    """Compare two texts with several lexical metrics."""

    def __init__(self, language: str = "russian") -> None:
        """Ensure that required NLTK resources are available and
        initialise stop‑word list.

        Parameters
        ----------
        language: str, optional
            NLTK language code (default is ``"russian"``).
        """
        resources = [
            ("tokenizers/punkt", "punkt"),
            ("corpora/stopwords", "stopwords"),
        ]
        for path, package in resources:
            try:
                nltk.data.find(path)
            except LookupError:
                nltk.download(package, quiet=True)

        self.language = language
        self.stops = (
            set(stopwords.words(language)) if language in stopwords.fileids() else set()
        )

    # ------------------------------------------------------------------
    # Pre‑processing helpers
    # ------------------------------------------------------------------

    def preprocess_text(self, text: str, remove_stopwords: bool = False) -> List[str]:
        """Lower‑case, strip punctuation/digits, tokenise.

        The resulting list always contains *word* tokens; punctuation and
        numbers are removed. If *remove_stopwords* is ``True`` and a list
        exists for the chosen language, stop‑words are filtered out.
        """
        text = text.lower()
        text = re.sub(r"[^\w\s]|[\d]", " ", text)
        tokens = word_tokenize(text, language=self.language)
        if remove_stopwords:
            tokens = [tok for tok in tokens if tok not in self.stops]
        return tokens

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    @staticmethod
    def _levenshtein_ops(ref: List[str], hyp: List[str]) -> Tuple[int, int, int]:
        """Return (substitutions, insertions, deletions) between *ref* and *hyp*."""
        m, n = len(ref), len(hyp)
        D = np.zeros((m + 1, n + 1), dtype=int)
        D[0, :] = np.arange(n + 1)
        D[:, 0] = np.arange(m + 1)

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if ref[i - 1] == hyp[j - 1] else 1
                D[i, j] = min(D[i - 1, j] + 1, D[i, j - 1] + 1, D[i - 1, j - 1] + cost)

        # back‑trace operations
        i, j = m, n
        subs = ins = dels = 0
        while i > 0 or j > 0:
            if i > 0 and j > 0 and ref[i - 1] == hyp[j - 1]:
                i, j = i - 1, j - 1
            elif i > 0 and j > 0 and D[i, j] == D[i - 1, j - 1] + 1:
                subs += 1
                i, j = i - 1, j - 1
            elif j > 0 and D[i, j] == D[i, j - 1] + 1:
                ins += 1
                j -= 1
            else:
                dels += 1
                i -= 1

        return subs, ins, dels

    def word_error_rate(self, reference: List[str], hypothesis: List[str]) -> Tuple[float, int, int, int]:
        subs, ins, dels = self._levenshtein_ops(reference, hypothesis)
        wer = (subs + ins + dels) / max(len(reference), 1)
        return wer, subs, ins, dels

    @staticmethod
    def cosine_sim(reference: str, hypothesis: str) -> float:
        vecs = TfidfVectorizer().fit_transform([reference, hypothesis])
        return cosine_similarity(vecs)[0, 1]

    @staticmethod
    def jaccard_similarity(seq1, seq2) -> float:
        s1, s2 = set(seq1), set(seq2)
        return len(s1 & s2) / max(len(s1 | s2), 1)

    # ------------------------------------------------------------------
    # Diagnostics / highlighting
    # ------------------------------------------------------------------

    @staticmethod
    def highlight_differences(reference: str, hypothesis: str) -> Dict[str, List[str]]:
        d = difflib.Differ()
        diff = list(d.compare(reference.split(), hypothesis.split()))
        return {
            "common_words": [w[2:] for w in diff if w.startswith("  ")],
            "missing_in_hypothesis": [w[2:] for w in diff if w.startswith("- ")],
            "extra_in_hypothesis": [w[2:] for w in diff if w.startswith("+ ")],
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, reference_text: str, hypothesis_text: str, *, detailed: bool = True):
        """Return a dict with WER, similarity scores and (optionally) details."""
        reference_raw = reference_text.strip()
        hypothesis_raw = hypothesis_text.strip()

        ref_tokens = self.preprocess_text(reference_raw)
        hyp_tokens = self.preprocess_text(hypothesis_raw)

        wer, subs, ins, dels = self.word_error_rate(ref_tokens, hyp_tokens)
        cosine = self.cosine_sim(reference_raw, hypothesis_raw)
        jaccard = self.jaccard_similarity(ref_tokens, hyp_tokens)

        correct_words = len(ref_tokens) - (subs + dels)
        word_accuracy = correct_words / max(len(ref_tokens), 1)
        recognition_completeness = 1 - dels / max(len(ref_tokens), 1)

        result = {
            "word_error_rate": wer,
            "word_accuracy": word_accuracy,
            "cosine_similarity": cosine,
            "jaccard_similarity": jaccard,
            "recognition_completeness": recognition_completeness,
            "error_details": {
                "substitutions": subs,
                "insertions": ins,
                "deletions": dels,
            },
            "reference_word_count": len(ref_tokens),
            "transcript_word_count": len(hyp_tokens),
        }

        if detailed:
            diff = self.highlight_differences(reference_raw, hypothesis_raw)
            result["differences"] = diff

            accuracy_score = 100 * (1 - wer)
            similarity_score = 100 * (0.6 * cosine + 0.4 * jaccard)
            overall = 0.7 * accuracy_score + 0.3 * similarity_score

            result["scores"] = {
                "accuracy_score": round(accuracy_score, 1),
                "similarity_score": round(similarity_score, 1),
                "overall_score": round(overall, 1),
            }

            if overall >= 90:
                quality = "Отлично"
            elif overall >= 75:
                quality = "Хорошо"
            elif overall >= 60:
                quality = "Удовлетворительно"
            else:
                quality = "Требуется улучшение"
            result["quality_assessment"] = quality

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