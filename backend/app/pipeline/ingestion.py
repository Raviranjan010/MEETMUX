"""
Data ingestion pipeline: parse CSV/JSON uploads → validate → clean → persist.
FR-1 implementation.
"""
import csv
import io
import json
import logging
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.models import Flight, AuditRecord
from app.models.enums import AuditAction
from app.pipeline.validation import validate_flight_batch
from app.pipeline.cleaning import clean_and_normalize_flights
from app.schemas.pipeline import IngestionSummary, RowValidationDetail

logger = logging.getLogger(__name__)


def parse_upload_content(content: bytes, filename: str) -> List[Dict[str, Any]]:
    """Parses raw file content into a list of row dictionaries."""
    text = content.decode("utf-8")

    if filename.lower().endswith(".json"):
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("flights", [data])
        if not isinstance(data, list):
            raise ValueError("JSON must be an array of flight objects or {flights: [...]}")
        return data

    # CSV
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        cleaned = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}
        rows.append(cleaned)
    return rows


def ingest_flights(raw_rows: List[Dict[str, Any]], db: Session) -> IngestionSummary:
    """
    Full ingestion pipeline: validate → clean → persist.
    Returns structured summary with per-row errors.
    """
    accepted_rows, validation_errors = validate_flight_batch(raw_rows, db)

    error_details = [
        RowValidationDetail(
            row_number=e.row_number,
            flight_number=e.flight_number,
            error_code=e.error_code,
            message=e.message,
            field=e.field,
        )
        for e in validation_errors
    ]

    if not accepted_rows:
        return IngestionSummary(
            total_rows=len(raw_rows),
            accepted_rows=0,
            rejected_rows=len(validation_errors),
            accepted_flight_ids=[],
            errors=error_details,
        )

    # Clean and normalize
    cleaned = clean_and_normalize_flights(accepted_rows, db)

    # Persist flights
    created_ids = []
    for item in cleaned:
        flight = Flight(**item)
        db.add(flight)
        db.flush()
        created_ids.append(str(flight.id))

    audit = AuditRecord(
        action=AuditAction.DATA_UPLOAD,
        actor="operator",
        details={
            "accepted_count": len(created_ids),
            "rejected_count": len(validation_errors),
            "total_rows": len(raw_rows),
        },
    )
    db.add(audit)
    db.commit()
    logger.info(f"Ingested {len(created_ids)} flights, rejected {len(validation_errors)}")

    return IngestionSummary(
        total_rows=len(raw_rows),
        accepted_rows=len(created_ids),
        rejected_rows=len(validation_errors),
        accepted_flight_ids=created_ids,
        errors=error_details,
    )
