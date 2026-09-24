from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.base import CommonMixin, GUID
from app.models.enums import ScenarioType, RiskLevel

JSONType = JSON().with_variant(JSONB, "postgresql")


class Scenario(CommonMixin, Base):
    __tablename__ = "scenarios"

    type = Column(Enum(ScenarioType), nullable=False)
    target_reference = Column(Text, nullable=False)
    params = Column(JSONType, nullable=False)
    applied_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False,
    )
    resulting_optimization_run_id = Column(
        GUID(),
        ForeignKey("optimization_runs.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
    )

    optimization_runs = relationship(
        "OptimizationRun",
        foreign_keys="OptimizationRun.scenario_id",
        back_populates="scenario",
    )
    cascade_events = relationship("CascadeEvent", back_populates="scenario")


class CascadeEvent(CommonMixin, Base):
    __tablename__ = "cascade_events"

    root_flight_id = Column(GUID(), ForeignKey("flights.id", ondelete="SET NULL"), nullable=True, index=True)
    root_gate_id = Column(GUID(), ForeignKey("gates.id", ondelete="SET NULL"), nullable=True, index=True)
    root_runway_id = Column(GUID(), ForeignKey("runways.id", ondelete="SET NULL"), nullable=True, index=True)
    scenario_id = Column(GUID(), ForeignKey("scenarios.id", ondelete="SET NULL"), nullable=True, index=True)
    propagation_path = Column(JSONType, nullable=False)
    affected_flight_ids = Column(JSONType, nullable=False)
    severity = Column(Enum(RiskLevel), nullable=False)

    scenario = relationship("Scenario", back_populates="cascade_events")
    root_flight = relationship("Flight", foreign_keys=[root_flight_id])
    root_gate = relationship("Gate", foreign_keys=[root_gate_id])
    root_runway = relationship("Runway", foreign_keys=[root_runway_id])
