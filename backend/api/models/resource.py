from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.app.extensions import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False) # e.g. 'Anxiety', 'Sleep Issues', etc.
    content = Column(Text, nullable=False)
    tags = Column(String, nullable=True) # comma separated
    created_at = Column(DateTime, default=datetime.utcnow)
