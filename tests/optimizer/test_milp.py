import pytest
from app.core.db import SessionLocal
from app.models import OptimizationRun
from app.models.enums import RunType, SolverUsed, OptimizationStatus
from app.optimizer.milp import run_milp_optimization, _check_ortools


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_ortools_installed():
    assert _check_ortools() is True


def test_milp_optimization_run(db):
    result = run_milp_optimization(db)

    assert result["run_type"] == "MILP"
    assert result["status"] in ["OPTIMAL", "FEASIBLE"]
    assert result["solver_used"] in ["GUROBI", "ORTOOLS"]
    assert "objective_value" in result
    assert result["objective_value"] >= 0.0
    assert result["solve_time_ms"] >= 0
    assert result["validation_passed"] is True
    assert result["assigned"] > 0
    assert result["total_flights"] >= 100

    # Verify DB persistence
    run_id = result["optimization_run_id"]
    run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    assert run is not None
    assert run.run_type == RunType.MILP
    assert run.validation_passed is True
    assert len(run.assignments) >= 100
