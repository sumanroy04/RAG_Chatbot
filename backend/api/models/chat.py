from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.app.extensions import Base

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    mood = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
