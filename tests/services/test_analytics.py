import pytest
from app.core.db import SessionLocal
from app.services.analytics import get_live_analytics, get_comparison_analytics
from app.services.baseline import run_baseline
from app.optimizer.milp import run_milp_optimization


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_live_analytics(db):
    analytics = get_live_analytics(db)
    assert "total_flights" in analytics
    assert analytics["total_flights"] >= 100
    assert "total_gates" in analytics
    assert analytics["total_gates"] == 30
    assert "fleet_utilization" in analytics
    assert "risk_distribution" in analytics


def test_comparison_analytics(db):
    # Ensure a baseline run and a MILP run exist
    b_res = run_baseline(db)
    m_res = run_milp_optimization(db)

    comp = get_comparison_analytics(db, m_res["optimization_run_id"])
    assert "baseline" in comp
    assert "optimized" in comp
    assert "deltas" in comp
    assert comp["baseline"]["total_flights"] >= 100
    assert comp["optimized"]["total_flights"] >= 100
    assert "conflict_count" in comp["baseline"]
    assert "conflict_count" in comp["optimized"]
