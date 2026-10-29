from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False) # overlap, pending_reminder, escalation, sla_warning
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    target_bureau_or_user = Column(String, nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="alerts")
