from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False, index=True)
    officer = Column(String, nullable=False)
    bureau_cell = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    remarks = Column(Text, nullable=False)
    attached_documents = Column(String, nullable=True) # comma-separated or json string
    transfer_escalation_info = Column(String, nullable=True)

    case = relationship("Case", back_populates="timeline_events")
