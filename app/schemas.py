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