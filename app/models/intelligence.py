from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class Intelligence(Base):
    __tablename__ = "intelligence"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"))
    category = Column(String)  # summary, correlation, risk_score, metadata, etc.
    content = Column(String)   # AI-generated text
    created_at = Column(DateTime, default=datetime.utcnow)
