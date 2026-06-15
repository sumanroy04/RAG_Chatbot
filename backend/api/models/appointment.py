from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from backend.app.extensions import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True) # Optional link to registered user
    therapist_name = Column(String, nullable=False)
    date_time = Column(String, nullable=False) # e.g. '2026-06-16 10:00'
    status = Column(String, default="Scheduled") # Scheduled, Completed, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
