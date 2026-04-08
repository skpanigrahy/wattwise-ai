from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from backend.db.session import Base

class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    model = Column(String, index=True)
    source = Column(String)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    cost = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)