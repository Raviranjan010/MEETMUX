import pytest
from app.core.db import SessionLocal
from app.models import GateAssignment
from app.services.explain import explain_assignment
from app.optimizer.milp import run_milp_optimization


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_explain_assignment_facts(db):
    # Ensure a MILP run exists
    run_milp_optimization(db)

    ga = db.query(GateAssignment).filter(GateAssignment.gate_id.isnot(None)).first()
    assert ga is not None

    # Test explain by assignment ID
    exp = explain_assignment(db, str(ga.id))
    assert "error" not in exp
    assert exp["flight_number"] == ga.flight.flight_number
    assert exp["assigned_gate"] == ga.gate.code
    assert len(exp["reasons"]) > 0
    assert len(exp["hard_constraints_satisfied"]) >= 3
    assert "alternatives_evaluated" in exp

    # Test explain by flight ID
    exp2 = explain_assignment(db, str(ga.flight_id))
    assert "error" not in exp2
    assert exp2["flight_number"] == ga.flight.flight_number
