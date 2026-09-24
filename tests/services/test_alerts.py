import pytest
from app.core.db import SessionLocal
from app.models import Alert
from app.services.alerts import generate_alerts_from_state, get_alerts


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_alerts_generation_and_query(db):
    new_alerts = generate_alerts_from_state(db)
    all_alerts = get_alerts(db)
    assert isinstance(all_alerts, list)

    if all_alerts:
        a = all_alerts[0]
        assert "id" in a
        assert "severity" in a
        assert "message" in a
        assert "resolved" in a
