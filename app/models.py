import math
from typing import List, Tuple

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Date, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class PulseMeasurement(Base):
    __tablename__ = "pulse_measurements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    value = Column(Integer, nullable=False)
    measured_at = Column(DateTime, nullable=False)
    created_at = Column(Date, default=date.today)
    __table_args__ = (UniqueConstraint('user_id', 'measured_at', name='_user_measured_uc'),)


class ShtangeTestResult(Base):
    __tablename__ = "shtange_test_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    heart_rate_before = Column(Integer, nullable=False)
    breath_hold_seconds = Column(Integer, nullable=False)
    heart_rate_after = Column(Integer, nullable=False)
    test_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    result_estimation = Column(String, nullable=True)
    reaction_indicator = Column(Float, nullable=True)

    @classmethod
    def calculate_reaction_indicator(cls, heart_rate_after, heart_rate_before):
        if heart_rate_before == 0:
            return None
        return heart_rate_after / heart_rate_before

    @classmethod
    def calculate_result_estimation(cls, breath_hold_seconds):
        if breath_hold_seconds < 39:
            return "BAD"
        elif breath_hold_seconds > 50:
            return "GOOD"
        return "MEDIUM"

class RufieTestResult(Base):
    __tablename__ = "rufie_test_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    measurement_first = Column(Integer, nullable=False)
    measurement_second = Column(Integer, nullable=False)
    measurement_third = Column(Integer, nullable=False)
    test_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Новые поля
    rufie_index = Column(Float, nullable=True)
    result_estimation = Column(String, nullable=True)

    @classmethod
    def calculate_rufie_index(cls, measurement_first, measurement_second, measurement_third):
        return ((measurement_first + measurement_second + measurement_third) - 200) / 10

    @classmethod
    def calculate_result_estimation(cls, rufie_index):
        if rufie_index > 15:
            return "LOW"
        elif rufie_index <= 0:
            return "HIGH"
        elif 0.5 <= rufie_index <= 5:
            return "MEDIUM_HIGH"
        elif 6 <= rufie_index <= 10:
            return "MEDIUM"
        elif 11 <= rufie_index <= 15:
            return "MEDIUM_LOW"
        return "UNKNOWN"

class StrupTestResult(Base):
    __tablename__ = "strup_test_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    result = Column(Integer, nullable=False)
    test_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)
    result_estimation = Column(String, nullable=True)

    @classmethod
    def calculate_result_estimation(cls, result):
        if result < 10:
            return "BAD"
        elif result > 16:
            return "GOOD"
        return "MEDIUM"

class PersonalReportTestResult(Base):
    __tablename__ = "personal_report_test_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    performance_measure = Column(Integer, nullable=False)
    test_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Новые поля
    days_comparison = Column(String, nullable=False)  # LOT_WORSE, WORSE, SAME, BETTER, LOT_BETTER


class EscalTestResult(Base):
    __tablename__ = "escal_test_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    result_text = Column(Text, nullable=False)
    test_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

class EscalResults(Base):
    __tablename__ = "escal_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    v1_result = Column(Integer, nullable=True)
    v1_v2_result = Column(Integer, nullable=True)
    v2_result = Column(Integer, nullable=True)
    v2_v3_result = Column(Integer, nullable=True)
    v3_result = Column(Integer, nullable=True)
    v3_v4_result = Column(Integer, nullable=True)
    v4_result = Column(Integer, nullable=True)
    v4_v1_result = Column(Integer, nullable=True)

    # Для связи с пользователем
    user = relationship("User", back_populates="escal_results")

class GenchTestResult(Base):
    __tablename__ = "gench_test_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    heart_rate_before = Column(Integer, nullable=False)
    breath_hold_seconds = Column(Integer, nullable=False)
    heart_rate_after = Column(Integer, nullable=False)
    test_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Новые поля
    result_estimation = Column(String, nullable=True)  # BAD, MEDIUM, GOOD
    reaction_indicator = Column(Float, nullable=True)

    @classmethod
    def calculate_reaction_indicator(cls, heart_rate_after, heart_rate_before):
        if heart_rate_before == 0:  # Предотвращаем деление на 0
            return None
        return heart_rate_after / heart_rate_before

    @classmethod
    def calculate_result_estimation(cls, breath_hold_seconds):
        if breath_hold_seconds < 24:
            return "BAD"
        elif breath_hold_seconds > 40:
            return "GOOD"
        return "MEDIUM"


class ReactionsTestResult(Base):
    __tablename__ = "reactions_test_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    visual = Column(String, nullable=True)  # Список пар времени реакции (JSON)
    audio = Column(String, nullable=True)  # Список пар времени реакции (JSON)
    test_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    visual_errors = Column(Integer, default=0)
    audio_errors = Column(Integer, default=0)
    visual_average_diff = Column(Float, default=0.0)
    audio_average_diff = Column(Float, default=0.0)
    visual_quav_diff = Column(Float, default=0.0)
    audio_quav_diff = Column(Float, default=0.0)

    # Добавляем связь с User
    user = relationship("User", back_populates="reactions_test_results")

    @classmethod
    def calculate_errors(cls, reactions: List[Tuple[int, int]]) -> int:
        errors = 0
        for pair in reactions:
            if abs(pair[0] - pair[1]) > 1000:
                errors += 1
        return errors

    @classmethod
    def calculate_average_diff(cls, reactions: List[Tuple[int, int]]) -> int:
        errors = 0
        for pair in reactions:
            if abs(pair[0] - pair[1]) > 1000:
                errors += 1
        return errors

    @classmethod
    def mean_std_difference(cls, pairs: List[Tuple[int, int]]) -> Tuple[float, float]:
        if not pairs:
            return (0.0, 0.0)

        differences = [abs(a - b) for a, b in pairs]
        n = len(differences)
        mean = sum(differences) / n

        variance = sum((x - mean) ** 2 for x in differences) / (n - 1 if n > 1 else 1)
        std = math.sqrt(variance)

        return mean, std


class EscalDailyResults(Base):
    __tablename__ = "escal_daily_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    performance = Column(Integer, nullable=False)
    fatigue = Column(Integer, nullable=False)
    anxiety = Column(Integer, nullable=False)
    conflict = Column(Integer, nullable=False)
    autonomy = Column(Integer, nullable=False)
    heteron = Column(Integer, nullable=False)
    eccentricity = Column(Integer, nullable=False)
    concetration = Column(Integer, nullable=False)
    vegeative = Column(Integer, nullable=False)
    wellbeingX = Column(Integer, nullable=False)
    wellbeingZ = Column(Float, nullable=False)
    activityX = Column(Integer, nullable=False)
    activityZ = Column(Float, nullable=False)
    moodX = Column(Integer, nullable=False)
    moodZ = Column(Float, nullable=False)
    ipX = Column(Integer, nullable=False)
    ipZ = Column(Float, nullable=False)
    test_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Для связи с пользователем
    user = relationship("User", back_populates="escal_daily_results")


class TextAuditionResults(Base):
    __tablename__ = "text_audition_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    read_text_path = Column(String, nullable=False)
    repeat_text_path = Column(String, nullable=False)
    test_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    quality_score_read = Column(Float)
    quality_score_repeat = Column(Float)
    pauses_count_read = Column(Integer)
    pauses_count_repeat = Column(Integer)
    average_volume_read = Column(Float)
    average_volume_repeat = Column(Float)

    # Для связи с пользователем
    user = relationship("User", back_populates="text_audition_results")


User.text_audition_results = relationship("TextAuditionResults", back_populates="user", uselist=False)
User.escal_daily_results = relationship("EscalDailyResults", back_populates="user", uselist=False)
User.reactions_test_results = relationship("ReactionsTestResult", back_populates="user", uselist=False)
User.escal_results = relationship("EscalResults", back_populates="user", uselist=False)