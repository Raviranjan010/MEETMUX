from sqlalchemy import Column, Text, Boolean, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.base import CommonMixin, GUID
from app.models.enums import AlertSeverity, AlertCategory


class Alert(CommonMixin, Base):
    __tablename__ = "alerts"

    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    category = Column(Enum(AlertCategory), nullable=False, index=True)
    flight_id = Column(GUID(), ForeignKey("flights.id", ondelete="SET NULL"), nullable=True, index=True)
    gate_id = Column(GUID(), ForeignKey("gates.id", ondelete="SET NULL"), nullable=True, index=True)
    message = Column(Text, nullable=False)
    resolved = Column(Boolean, nullable=False, default=False, index=True)

    __table_args__ = (
        Index("ix_alerts_resolved_severity", "resolved", "severity"),
    )

    flight = relationship("Flight", back_populates="alerts")
    gate = relationship("Gate", back_populates="alerts")
