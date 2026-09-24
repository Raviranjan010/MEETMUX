from sqlalchemy import Column, String, Integer, Numeric, Boolean, Enum, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.base import CommonMixin, GUID
from app.models.enums import RunType, SolverUsed, OptimizationStatus, AssignmentStatus

JSONType = JSON().with_variant(JSONB, "postgresql")


class OptimizationRun(CommonMixin, Base):
    __tablename__ = "optimization_runs"

    run_type = Column(Enum(RunType), nullable=False)
    scenario_id = Column(GUID(), ForeignKey("scenarios.id", ondelete="SET NULL"), nullable=True, index=True)
    solver_used = Column(Enum(SolverUsed), nullable=False)
    solver_status = Column(String(32), nullable=False)
    status = Column(Enum(OptimizationStatus), nullable=False, index=True)
    objective_value = Column(Numeric(12, 3), nullable=True)
    solve_time_ms = Column(Integer, nullable=True)
    validation_passed = Column(Boolean, nullable=True)
    validation_report = Column(JSONType, nullable=True)
    config_snapshot = Column(JSONType, nullable=False)

    __table_args__ = (
        Index("ix_opt_runs_status_created", "status", "created_at"),
    )

    scenario = relationship("Scenario", foreign_keys=[scenario_id], back_populates="optimization_runs")
    assignments = relationship("GateAssignment", back_populates="optimization_run", cascade="all, delete-orphan")


class GateAssignment(CommonMixin, Base):
    __tablename__ = "gate_assignments"

    optimization_run_id = Column(GUID(), ForeignKey("optimization_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    flight_id = Column(GUID(), ForeignKey("flights.id", ondelete="RESTRICT"), nullable=False, index=True)
    gate_id = Column(GUID(), ForeignKey("gates.id", ondelete="RESTRICT"), nullable=True, index=True)
    assignment_status = Column(Enum(AssignmentStatus), nullable=False, index=True)
    objective_contribution = Column(Numeric(10, 3), nullable=True)

    __table_args__ = (
        UniqueConstraint("optimization_run_id", "flight_id", name="uq_gate_assignments_run_flight"),
        Index("ix_gate_assignments_gate_status", "gate_id", "assignment_status"),
    )

    optimization_run = relationship("OptimizationRun", back_populates="assignments")
    flight = relationship("Flight", back_populates="gate_assignments")
    gate = relationship("Gate", back_populates="assignments")
