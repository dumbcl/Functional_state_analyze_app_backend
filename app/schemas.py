from datetime import datetime, date
from typing import List, Tuple, Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PulseIn(BaseModel):
    value: int
    measured_at: datetime

class PulseResponse(BaseModel):
    value: int
    measured_at: datetime
    created_at: datetime

class ShtangeTestIn(BaseModel):
    heart_rate_before: int
    breath_hold_seconds: int
    heart_rate_after: int

class EscalTestIn(BaseModel):
    result_text: str

class AvailableTest(BaseModel):
    type: str
    last_test_date: Optional[str] = None  # Добавляем дату последнего прохождения теста (необязательное поле)

    class Config:
        orm_mode = True

class AvailableTestsResponse(BaseModel):
    available_tests: List[AvailableTest]
    completed_tests: List[AvailableTest]

class EscalResultsCreate(BaseModel):
    v1_result: int
    v1_v2_result: int
    v2_result: int
    v2_v3_result: int
    v3_result: int
    v3_v4_result: int
    v4_result: int
    v4_v1_result: int

class EscalResultsResponse(EscalResultsCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class ReactionsTestResultsCreate(BaseModel):
    visual: List[Tuple[int, int]]  # Список пар для visual
    audio: List[Tuple[int, int]]   # Список пар для audio

class ReactionsTestResultsResponse(ReactionsTestResultsCreate):
    id: int
    user_id: int
    test_date: str
    created_at: str
    visual_errors: int
    audio_errors: int

    class Config:
        orm_mode = True

# app/schemas.py
class GenchTestResultCreate(BaseModel):
    heart_rate_before: int
    breath_hold_seconds: int
    heart_rate_after: int

class GenchTestResultResponse(GenchTestResultCreate):
    id: int
    user_id: int
    result_estimation: str
    reaction_indicator: float
    test_date: str
    created_at: str

    class Config:
        orm_mode = True

class RufieTestResultCreate(BaseModel):
    measurement_first: int
    measurement_second: int
    measurement_third: int

class RufieTestResultResponse(RufieTestResultCreate):
    id: int
    user_id: int
    rufie_index: float
    result_estimation: str
    test_date: str
    created_at: str

    class Config:
        orm_mode = True

class StrupTestResultCreate(BaseModel):
    result: int

class StrupTestResultResponse(StrupTestResultCreate):
    id: int
    user_id: int
    result_estimation: str
    test_date: str
    created_at: str

    class Config:
        orm_mode = True

class PersonalReportTestResultCreate(BaseModel):
    performance_measure: int
    days_comparison: str  # LOT_WORSE, WORSE, SAME, BETTER, LOT_BETTER

class PersonalReportTestResultResponse(PersonalReportTestResultCreate):
    id: int
    user_id: int
    test_date: str
    created_at: str

    class Config:
        orm_mode = True

class EscalDailyResultsCreate(BaseModel):
    performance: int
    fatigue: int
    anxiety: int
    conflict: int
    autonomy: int
    heteron: int
    eccentricity: int
    concetration: int
    vegeative: int
    wellbeingX: int
    wellbeingZ: float
    activityX: int
    activityZ: float
    moodX: int
    moodZ: float
    ipX: int
    ipZ: float

class EscalDailyResultsResponse(EscalDailyResultsCreate):
    id: int
    user_id: int
    test_date: str
    created_at: str

    class Config:
        orm_mode = True

class TextAuditionResponse(BaseModel):
    read_text: str
    repeat_text: str

    class Config:
        orm_mode = True

class TextAuditionResultResponse(BaseModel):
    read_text_path: str
    repeat_text_path: str
    test_date: str
    created_at: str
    mistakes_percentage_read: float = 0.0
    mistakes_percentage_repeat: float = 0.0
    pauses_count_read: int = 0
    pauses_count_repeat: int = 0
    average_volume_read: float = 0.0
    average_volume_repeat: float = 0.0

    class Config:
        orm_mode = True

class ShtangeTestResult(BaseModel):
    shtange_result: str
    shtange_result_indicator: float
    shtange_test_result_indicator_average: float
    type: str

class PulseMeasurementResult(BaseModel):
    pulseAverage: float
    pulseMax: int
    pulseMin: int
    type: str

    class Config:
        orm_mode = True

class RufieTestResult(BaseModel):
    rufie_result: str
    rufie_result_indicator: int
    rufie_test_result_indicator_average: float
    type: str

    class Config:
        orm_mode = True

class StrupTestResult(BaseModel):
    strup_result_estimation: str
    strup_result: int
    strup_test_result_average: float
    type: str

    class Config:
        orm_mode = True

class GenchTestResult(BaseModel):
    gench_result_estimation: str
    gench_result_indicator: float
    gench_test_result_indicator_average: float
    type: str

    class Config:
        orm_mode = True

class ReactionsTestResult(BaseModel):
    reactions_visual_errors: int
    reactions_audio_errors: int
    reactions_visual_errors_average: float
    reactions_audio_errors_average: float
    reactions_visual_errors_type: str
    reactions_audio_errors_type: str

    class Config:
        orm_mode = True

class TextAuditionTestResult(BaseModel):
    pauses_count_read: int
    pauses_count_repeat: int
    pauses_count_read_average: float
    pauses_count_repeat_average: float
    average_volume_read: float
    average_volume_repeat: float
    average_volume_read_average: float
    average_volume_repeat_average: float
    pauses_count_read_type: str
    pauses_count_repeat_type: str

    class Config:
        orm_mode = True

class PersonalReportTestResult(BaseModel):
    personal_report_about_day: str
    personal_report_current: int
    personal_report_current_average: float
    type: str

    class Config:
        orm_mode = True

class DailyTestResult(BaseModel):
    date: str
    shtange_test_result: Optional[ShtangeTestResult] = None
    personal_report: Optional[PersonalReportTestResult] = None
    pulse_measurement: Optional[PulseMeasurementResult] = None
    rufie_test_result: Optional[RufieTestResult] = None
    strup_test_result: Optional[StrupTestResult] = None
    gench_test_result: Optional[GenchTestResult] = None
    reactions_test_result: Optional[ReactionsTestResult] = None
    text_audition_test_result: Optional[TextAuditionTestResult] = None
    day_description: Optional[str]
    day_type: Optional[str]

    class Config:
        orm_mode = True

