from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base

class Institution(Base):
    __tablename__ = "institutions"

    permanent_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False)
    region = Column(String, nullable=False, index=True)
    pincode = Column(String, nullable=False, index=True)

    cases = relationship("Case", back_populates="institution")
    overlap_flags = relationship("OverlapFlag", back_populates="institution")
