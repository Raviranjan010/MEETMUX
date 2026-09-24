import io
import csv
import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models import Flight, AuditRecord
from app.models.enums import AuditAction
from app.pipeline.validation import validate_flight_batch, ValidationErrorItem
from app.pipeline.cleaning import clean_and_normalize_flights
from app.schemas.pipeline import IngestionSummary, RowValidationDetail


def parse_upload_content(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Parses uploaded file content (CSV or JSON) into a list of row dicts."""
    text = file_bytes.decode("utf-8-sig")

    if filename.endswith(".json") or text.strip().startswith("[") or text.strip().startswith("{"):
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return [parsed]
        elif isinstance(parsed, list):
            return parsed
        else:
            raise ValueError("Invalid JSON format. Expected list of flight objects.")

    # Otherwise parse as CSV
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise ValueError("Malformed CSV: header row is missing or empty.")

    rows: List[Dict[str, Any]] = []
    for row in reader:
        # Strip keys and values
        clean_row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k is not None}
        rows.append(clean_row)
    return rows


def ingest_flights(
    raw_rows: List[Dict[str, Any]],
    db: Session,
) -> IngestionSummary:
    """
    Validates, cleans, and ingests flights.
    Persists accepted rows and records an audit log.
    Returns IngestionSummary.
    """
    accepted_rows, validation_errors = validate_flight_batch(raw_rows, db)

    accepted_flight_ids = []
    if accepted_rows:
        cleaned_records = clean_and_normalize_flights(accepted_rows, db)
        for item in cleaned_records:
            flight = Flight(**item)
            db.add(flight)
            db.flush()
            accepted_flight_ids.append(str(flight.id))

        # Record audit log per requirements
        audit = AuditRecord(
            action=AuditAction.DATA_UPLOAD,
            actor="operator",
            details={
                "total_rows": len(raw_rows),
                "accepted_count": len(accepted_rows),
                "rejected_count": len(validation_errors),
                "flight_ids": accepted_flight_ids,
            },
        )
        db.add(audit)
        db.commit()

    error_details = [
        RowValidationDetail(
            row_number=err.row_number,
            flight_number=err.flight_number,
            error_code=err.error_code,
            message=err.message,
            field=err.field,
        )
        for err in validation_errors
    ]

    return IngestionSummary(
        total_rows=len(raw_rows),
        accepted_rows=len(accepted_rows),
        rejected_rows=len(validation_errors),
        accepted_flight_ids=accepted_flight_ids,
        errors=error_details,
    )
