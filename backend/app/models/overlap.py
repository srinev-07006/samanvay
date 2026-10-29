from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class OverlapFlag(Base):
    __tablename__ = "overlap_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_a_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    case_b_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    institution_id = Column(String, ForeignKey("institutions.permanent_id"), nullable=False, index=True)
    confidence_score = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
    state = Column(String, default="Open", nullable=False) # Open, Linked, Mapped, Dismissed
    decided_by = Column(String, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    institution = relationship("Institution", back_populates="overlap_flags")
