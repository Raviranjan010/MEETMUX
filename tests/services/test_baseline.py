import pytest
from app.core.db import SessionLocal
from app.models import OptimizationRun
from app.models.enums import RunType, OptimizationStatus
from app.services.baseline import run_baseline


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_baseline_deterministic_run(db):
    result1 = run_baseline(db)
    assert result1["status"] in ["OPTIMAL", "FEASIBLE"]
    assert result1["run_type"] == "BASELINE"
    assert result1["total_flights"] >= 100
    assert result1["assigned"] > 0

    run_id = result1["optimization_run_id"]
    run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    assert run is not None
    assert run.run_type == RunType.BASELINE
    assert len(run.assignments) == result1["total_flights"]
