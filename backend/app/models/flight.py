from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base


class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(20), index=True, nullable=False)
    airline = Column(String(50), index=True, nullable=False)
    aircraft_type = Column(String(20), nullable=False)  # e.g., 'A320', 'B737', 'B777', 'A350', 'B787'
    origin = Column(String(10), nullable=False)
    destination = Column(String(10), nullable=False)
    terminal = Column(String(10), nullable=False)  # e.g., 'T1', 'T2', 'T3'
    
    scheduled_arrival = Column(DateTime, nullable=False, index=True)
    estimated_arrival = Column(DateTime, nullable=True)
    actual_arrival = Column(DateTime, nullable=True)
    
    scheduled_departure = Column(DateTime, nullable=False, index=True)
    estimated_departure = Column(DateTime, nullable=True)
    actual_departure = Column(DateTime, nullable=True)
    
    runway = Column(String(20), nullable=True)
    taxi_in_minutes = Column(Float, default=0.0)
    taxi_out_minutes = Column(Float, default=0.0)
    turnaround_minutes = Column(Float, default=45.0)
    status = Column(String(30), default="Scheduled", index=True)  # Scheduled, Arrived, Delayed, Boarding, Departed
    
    # Relationships
    predictions = relationship("DelayPrediction", back_populates="flight", cascade="all, delete-orphan")
    gate_assignments = relationship("GateAssignment", back_populates="flight", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_flight_scheduled_times", "scheduled_arrival", "scheduled_departure"),
    )
