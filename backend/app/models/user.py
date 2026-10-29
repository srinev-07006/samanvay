from sqlalchemy import Column, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # e.g. username or uuid
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False) # RB, PGRC, Cell, RegionalOffice, SeniorManagement, CompetentAuthority
    bureau_cell = Column(String, nullable=True) # Regulation Bureau, PGRC, Academic Cell, etc.
    region = Column(String, nullable=True) # North, South, East, West, Central, etc.
    is_active = Column(Boolean, default=True)
