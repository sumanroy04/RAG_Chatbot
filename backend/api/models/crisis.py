from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.app.extensions import Base

class CrisisLog(Base):
    __tablename__ = "crisis_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    message = Column(Text, nullable=False)
    matched_keywords = Column(String, nullable=False) # Comma-separated trigger words
    created_at = Column(DateTime, default=datetime.utcnow)
