from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.database import Base


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(30), nullable=False)  # OPTIMAL, FEASIBLE, INFEASIBLE, TIMEOUT, ERROR
    solver = Column(String(30), nullable=False)  # ortools, gurobi
    objective_value = Column(Float, nullable=True)
    execution_time = Column(Float, nullable=False)  # in seconds
    total_flights = Column(Integer, nullable=False)
    total_gates = Column(Integer, nullable=False)
    assigned_flights = Column(Integer, default=0)
    unassigned_flights = Column(Integer, default=0)
    gates_utilized = Column(Integer, default=0)
    conflicts_count = Column(Integer, default=0)
    metrics_summary = Column(String(2000), nullable=True)  # JSON serialized metrics
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    assignments = relationship("GateAssignment", back_populates="optimization_run", cascade="all, delete-orphan")


class GateAssignment(Base):
    __tablename__ = "gate_assignments"

    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id", ondelete="CASCADE"), nullable=False, index=True)
    gate_id = Column(Integer, ForeignKey("gates.id", ondelete="CASCADE"), nullable=False, index=True)
    optimization_run_id = Column(Integer, ForeignKey("optimization_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    arrival_time = Column(DateTime, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    assignment_status = Column(String(30), default="Assigned")  # Assigned, In Conflict, Reassigned, Cleared
    is_reassigned = Column(Integer, default=0)
    passenger_walk_score = Column(Float, default=1.0)
    
    # Relationships
    flight = relationship("Flight", back_populates="gate_assignments")
    gate = relationship("Gate", back_populates="gate_assignments")
    optimization_run = relationship("OptimizationRun", back_populates="assignments")

    __table_args__ = (
        Index("idx_assignment_flight_gate", "flight_id", "gate_id"),
    )
