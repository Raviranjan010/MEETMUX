import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.errors import AppError
from app.pipeline.ingestion import parse_upload_content, ingest_flights
from app.schemas.pipeline import IngestionResponse, IngestionSummary

router = APIRouter(prefix="/data", tags=["Data Pipeline"])
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB per docs/SECURITY.md


@router.post("/upload", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_flight_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Ingests and validates flight schedules from CSV or JSON file.
    Returns 202 with per-row validation report or 422 if input contains validation errors.
    """
    filename = file.filename or "upload.csv"
    if not (filename.endswith(".csv") or filename.endswith(".json")):
        raise AppError(
            code="UNSUPPORTED_FILE_TYPE",
            message="Only .csv and .json files are supported.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise AppError(
            code="FILE_TOO_LARGE",
            message=f"File exceeds maximum allowed size of 5 MB ({len(content)} bytes).",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )

    try:
        raw_rows = parse_upload_content(content, filename)
    except Exception as e:
        raise AppError(
            code="MALFORMED_FILE",
            message=f"Could not parse file: {str(e)}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if not raw_rows:
        raise AppError(
            code="EMPTY_FILE",
            message="Uploaded file contains no data rows.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    summary: IngestionSummary = ingest_flights(raw_rows, db)

    # Per AC-P3: Malformed CSV is rejected with structured 422 naming the row and field
    if summary.rejected_rows > 0 and summary.accepted_rows == 0:
        first_err = summary.errors[0]
        raise AppError(
            code="VALIDATION_ERROR",
            message=f"Validation failed on row {first_err.row_number}: {first_err.message}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={
                "row_number": first_err.row_number,
                "field": first_err.field,
                "error_code": first_err.error_code,
                "all_errors": [err.model_dump() for err in summary.errors],
            },
        )

    return IngestionResponse(
        status="processed" if summary.rejected_rows == 0 else "partially_processed",
        summary=summary,
    )
