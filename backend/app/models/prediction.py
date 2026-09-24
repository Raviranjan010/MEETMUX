from sqlalchemy import Column, String, Numeric, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.base import CommonMixin, GUID
from app.models.enums import RiskLevel

# Use JSONB on PostgreSQL, JSON on others
JSONType = JSON().with_variant(JSONB, "postgresql")


class Prediction(CommonMixin, Base):
    __tablename__ = "predictions"

    flight_id = Column(GUID(), ForeignKey("flights.id", ondelete="RESTRICT"), nullable=False, index=True)
    model_version = Column(String(32), nullable=False)
    predicted_taxi_minutes = Column(Numeric(6, 2), nullable=False)
    predicted_delay_minutes = Column(Numeric(6, 2), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    feature_snapshot = Column(JSONType, nullable=False)

    flight = relationship("Flight", back_populates="predictions")
