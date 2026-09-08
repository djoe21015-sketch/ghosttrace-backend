from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from datetime import datetime
from app.database import Base

class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)

    # Basic identity
    name = Column(String, index=True)
    target_type = Column(String, index=True)  # email, domain, ip, username, phone, person
    value = Column(String, unique=True, index=True)

    # Raw extracted data before intelligence processing
    raw_data = Column(JSON, default={})

    # Intelligence results from all modules
    intelligence = Column(JSON, default={})

    # AI analysis output
    ai_summary = Column(String, default=None)
    risk_score = Column(Float, default=0.0)
    recommendations = Column(JSON, default={})

    # Status tracking
    status = Column(String, default="pending")  # pending, scanning, monitored, completed, error

    # Tags for grouping targets
    tags = Column(JSON, default=[])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
