from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False) # LOGIN, VIEW_CASE, CREATE_CASE, UPDATE_CASE, LINK_OVERLAP, DISMISS_OVERLAP
    entity = Column(String, nullable=False) # Case:C123, Institution:1-1234, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text, nullable=True)
