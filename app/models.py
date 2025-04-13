from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

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
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'measured_at', name='_user_measured_uc'),)

class ShtangeTestResult(Base):
    __tablename__ = "shtange_test_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    heart_rate_before = Column(Integer, nullable=False)
    breath_hold_seconds = Column(Integer, nullable=False)
    heart_rate_after = Column(Integer, nullable=False)
    test_date = Column(Date, default=datetime.utcnow().date)
    created_at = Column(DateTime, default=datetime.utcnow)

class EscalTestResult(Base):
    __tablename__ = "escal_test_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    result_text = Column(Text, nullable=False)
    test_date = Column(Date, default=datetime.utcnow().date)
    created_at = Column(DateTime, default=datetime.utcnow)

class Test(Base):
    __tablename__ = "tests"
    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)  # shtange, escal, etc.
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))

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