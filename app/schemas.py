from datetime import datetime, date
from typing import List
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