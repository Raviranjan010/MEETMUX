import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal
from app.models import OptimizationRun, GateAssignment, AuditRecord
from app.optimizer.milp import run_milp_optimization

client = TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_accept_and_reject_recommendation(db):
    opt_res = run_milp_optimization(db)
    run_id = opt_res["optimization_run_id"]

    # Test Accept
    accept_resp = client.post(f"/api/optimizer/{run_id}/accept")
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"

    # Verify audit record
    audit_accept = db.query(AuditRecord).filter(
        AuditRecord.action == "ASSIGNMENT_ACCEPT",
        AuditRecord.reference_id == run_id,
    ).first()
    assert audit_accept is not None

    # Test Reject
    reject_resp = client.post(f"/api/optimizer/{run_id}/reject")
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "rejected"

    audit_reject = db.query(AuditRecord).filter(
        AuditRecord.action == "ASSIGNMENT_REJECT",
        AuditRecord.reference_id == run_id,
    ).first()
    assert audit_reject is not None
