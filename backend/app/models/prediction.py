from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base


class DelayPrediction(Base):
    __tablename__ = "delay_predictions"

    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Direct flight fields for standalone/manual predictions
    flight_number = Column(String(20), nullable=True)
    predicted_delay_minutes = Column(Float, nullable=False)
    delay_category = Column(String(30), nullable=False)  # On Time, Low, Moderate, High, Severe
    confidence_score = Column(Float, nullable=True)
    contributing_features = Column(String(1000), nullable=True) # JSON or key:val string
    
    model_version = Column(String(50), default="1.0.0")
    prediction_timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    flight = relationship("Flight", back_populates="predictions")
