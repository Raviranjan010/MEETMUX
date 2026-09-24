from sqlalchemy import Column, String, Numeric, Enum, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.base import CommonMixin, GUID
from app.models.enums import GateType, AircraftSizeClass, GateEligibleRouteType, GateStatus


class Gate(CommonMixin, Base):
    __tablename__ = "gates"

    terminal_id = Column(GUID(), ForeignKey("terminals.id", ondelete="RESTRICT"), nullable=False, index=True)
    code = Column(String(8), nullable=False)
    gate_type = Column(Enum(GateType), nullable=False, index=True)
    max_aircraft_size = Column(Enum(AircraftSizeClass), nullable=False)
    eligible_route_types = Column(Enum(GateEligibleRouteType), nullable=False)
    status = Column(Enum(GateStatus), nullable=False, default=GateStatus.AVAILABLE, index=True)
    taxi_distance_meters = Column(Numeric(6, 1), nullable=False)

    __table_args__ = (
        UniqueConstraint("terminal_id", "code", name="uq_gates_terminal_code"),
        Index("ix_gates_status_gate_type", "status", "gate_type"),
    )

    terminal = relationship("Terminal", back_populates="gates")
    assignments = relationship("GateAssignment", back_populates="gate")
    alerts = relationship("Alert", back_populates="gate")
