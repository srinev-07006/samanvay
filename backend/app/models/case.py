from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String, primary_key=True, index=True)
    institution_id = Column(String, ForeignKey("institutions.permanent_id"), nullable=True, index=True)
    source_bureau = Column(String, nullable=False, index=True) # Regulation Bureau, PGRC, etc.
    category = Column(String, nullable=False, index=True) # faculty shortage, infrastructure, fee dispute, etc.
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, index=True) # Pending, Under Process, Disposed, Transferred
    current_bureau = Column(String, nullable=False)
    assigned_officer = Column(String, nullable=False)
    last_action = Column(String, nullable=False)
    next_action_required = Column(String, nullable=False)
    expected_disposal_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    institution = relationship("Institution", back_populates="cases")
    timeline_events = relationship("TimelineEvent", back_populates="case", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="case", cascade="all, delete-orphan")
