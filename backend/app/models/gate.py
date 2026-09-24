from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base


class Gate(Base):
    __tablename__ = "gates"

    id = Column(Integer, primary_key=True, index=True)
    gate_number = Column(String(20), unique=True, index=True, nullable=False)  # e.g., 'A01', 'B04', 'C12'
    terminal = Column(String(10), index=True, nullable=False)                  # e.g., 'T1', 'T2', 'T3'
    gate_type = Column(String(30), default="Contact")                         # Contact, Remote, Apron
    supported_aircraft_types = Column(String(255), nullable=False)             # Comma-separated or JSON string, e.g. "A320,B737,A321,B777"
    is_international = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    gate_assignments = relationship("GateAssignment", back_populates="gate")
