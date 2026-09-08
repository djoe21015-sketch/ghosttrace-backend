from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"))
    summary = Column(String)
    risk_score = Column(Integer)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
