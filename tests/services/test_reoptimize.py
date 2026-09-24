import pytest
from app.core.db import SessionLocal
from app.models import OptimizationRun, Scenario
from app.services.simulation import run_scenario, reset_scenarios
from app.services.reoptimize import reoptimize_after_scenario


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_reoptimize_pipeline_end_to_end(db):
    # 1. Apply scenario: Runway closure
    sc_res = run_scenario(db, "RUNWAY_CLOSURE", "RWY-2", {})
    scenario_id = sc_res["scenario_id"]

    initial_runs_count = db.query(OptimizationRun).count()

    # 2. Run re-optimization
    reopt_res = reoptimize_after_scenario(db, scenario_id=scenario_id)

    assert reopt_res["scenario_acknowledged"] is True
    assert "optimization_run_id" in reopt_res
    assert reopt_res["optimization_run_id"] is not None
    assert reopt_res["predictions_updated"] > 0
    assert len(reopt_res["steps"]) >= 5

    # Verify a new optimization run exists in the database
    new_runs_count = db.query(OptimizationRun).count()
    assert new_runs_count > initial_runs_count

    # Cleanup scenario state
    reset_scenarios(db)
