import io
import json
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal
from app.models import Flight, AuditRecord

client = TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_valid_csv_upload(db_session):
    # Prepare a valid flight CSV with unique flight number
    csv_content = (
        "flight_number,airline,aircraft_type_code,route_type,origin,destination,scheduled_arrival,scheduled_departure,runway_code\n"
        "VA9901,AA,A320,DOMESTIC,ORD,DFW,2026-11-01T10:00:00Z,2026-11-01T11:00:00Z,RWY-1\n"
    ).encode("utf-8")

    files = {"file": ("valid_flights.csv", csv_content, "text/csv")}
    response = client.post("/api/data/upload", files=files)

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "processed"
    assert data["summary"]["accepted_rows"] == 1
    assert data["summary"]["rejected_rows"] == 0
    assert len(data["summary"]["accepted_flight_ids"]) == 1

    # Verify flight exists in DB
    flight = db_session.query(Flight).filter_by(flight_number="VA9901").first()
    assert flight is not None
    assert flight.airline == "AA"
    assert flight.route_type.value == "DOMESTIC"
    assert flight.is_synthetic is True

    # Verify audit record created
    audit = db_session.query(AuditRecord).filter_by(action="DATA_UPLOAD").order_by(AuditRecord.created_at.desc()).first()
    assert audit is not None
    assert audit.details["accepted_count"] == 1

    # Clean up
    db_session.delete(flight)
    db_session.commit()


def test_malformed_timestamp_rejected():
    # AC-P3: Bad timestamp rejected with structured 422 error naming row and field
    bad_csv = (
        "flight_number,airline,aircraft_type_code,route_type,origin,destination,scheduled_arrival,scheduled_departure\n"
        "VA9902,AA,A320,DOMESTIC,ORD,DFW,INVALID_TIMESTAMP,2026-11-01T11:00:00Z\n"
    ).encode("utf-8")

    files = {"file": ("bad_timestamp.csv", bad_csv, "text/csv")}
    response = client.post("/api/data/upload", files=files)

    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["details"]["row_number"] == 1
    assert data["error"]["details"]["field"] == "scheduled_arrival"
    assert data["error"]["details"]["error_code"] == "MALFORMED_ROW"


def test_invalid_timestamp_order_rejected():
    # Departure earlier than arrival
    bad_csv = (
        "flight_number,airline,aircraft_type_code,route_type,origin,destination,scheduled_arrival,scheduled_departure\n"
        "VA9903,AA,A320,DOMESTIC,ORD,DFW,2026-11-01T12:00:00Z,2026-11-01T10:00:00Z\n"
    ).encode("utf-8")

    files = {"file": ("bad_order.csv", bad_csv, "text/csv")}
    response = client.post("/api/data/upload", files=files)

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["details"]["row_number"] == 1
    assert data["error"]["details"]["field"] == "scheduled_departure"
    assert data["error"]["details"]["error_code"] == "INVALID_TIMESTAMP_ORDER"


def test_missing_required_column_rejected():
    # AC-P3: Missing required column rejected with structured 422 naming field
    bad_csv = (
        "flight_number,airline,route_type,origin,destination,scheduled_arrival,scheduled_departure\n"
        "VA9904,AA,DOMESTIC,ORD,DFW,2026-11-01T10:00:00Z,2026-11-01T11:00:00Z\n"
    ).encode("utf-8")

    files = {"file": ("missing_col.csv", bad_csv, "text/csv")}
    response = client.post("/api/data/upload", files=files)

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["details"]["row_number"] == 1
    assert data["error"]["details"]["field"] == "aircraft_type_code"
    assert data["error"]["details"]["error_code"] == "MISSING_REQUIRED_FIELD"


def test_unknown_aircraft_type_rejected():
    bad_csv = (
        "flight_number,airline,aircraft_type_code,route_type,origin,destination,scheduled_arrival,scheduled_departure\n"
        "VA9905,AA,UNKNOWN_JET,DOMESTIC,ORD,DFW,2026-11-01T10:00:00Z,2026-11-01T11:00:00Z\n"
    ).encode("utf-8")

    files = {"file": ("unknown_ac.csv", bad_csv, "text/csv")}
    response = client.post("/api/data/upload", files=files)

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["details"]["row_number"] == 1
    assert data["error"]["details"]["field"] == "aircraft_type_code"
    assert data["error"]["details"]["error_code"] == "UNKNOWN_AIRCRAFT_TYPE"


def test_duplicate_flight_in_batch_rejected():
    # AC-P3: Duplicate flight rejected with structured 422
    duplicate_csv = (
        "flight_number,airline,aircraft_type_code,route_type,origin,destination,scheduled_arrival,scheduled_departure\n"
        "DUP101,AA,A320,DOMESTIC,ORD,DFW,2026-11-02T10:00:00Z,2026-11-02T11:00:00Z\n"
        "DUP101,AA,A320,DOMESTIC,ORD,DFW,2026-11-02T10:00:00Z,2026-11-02T11:30:00Z\n"
    ).encode("utf-8")

    files = {"file": ("duplicate_batch.csv", duplicate_csv, "text/csv")}
    response = client.post("/api/data/upload", files=files)

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["details"]["error_code"] == "DUPLICATE_FLIGHT"
    assert data["error"]["details"]["row_number"] == 2
    assert data["error"]["details"]["field"] == "flight_number"


def test_duplicate_flight_against_database_rejected(db_session):
    # Flight AA101 from seed exists in DB
    existing_flight = db_session.query(Flight).first()
    assert existing_flight is not None

    arr_iso = existing_flight.scheduled_arrival.isoformat()
    dep_iso = existing_flight.scheduled_departure.isoformat()

    dup_csv = (
        "flight_number,airline,aircraft_type_code,route_type,origin,destination,scheduled_arrival,scheduled_departure\n"
        f"{existing_flight.flight_number},{existing_flight.airline},A320,{existing_flight.route_type.value},DFW,ORD,{arr_iso},{dep_iso}\n"
    ).encode("utf-8")

    files = {"file": ("dup_db.csv", dup_csv, "text/csv")}
    response = client.post("/api/data/upload", files=files)

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["details"]["error_code"] == "DUPLICATE_FLIGHT"
    assert data["error"]["details"]["row_number"] == 1


def test_unsupported_file_extension():
    files = {"file": ("flights.txt", b"plain text content", "text/plain")}
    response = client.post("/api/data/upload", files=files)

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_json_upload_success(db_session):
    json_data = [
        {
            "flight_number": "JSON901",
            "airline": "DL",
            "aircraft_type_code": "B738",
            "route_type": "DOMESTIC",
            "origin": "ATL",
            "destination": "DFW",
            "scheduled_arrival": "2026-11-05T14:00:00Z",
            "scheduled_departure": "2026-11-05T15:15:00Z",
        }
    ]
    files = {"file": ("flights.json", json.dumps(json_data).encode("utf-8"), "application/json")}
    response = client.post("/api/data/upload", files=files)

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "processed"
    assert data["summary"]["accepted_rows"] == 1

    # Cleanup
    flight = db_session.query(Flight).filter_by(flight_number="JSON901").first()
    if flight:
        db_session.delete(flight)
        db_session.commit()
