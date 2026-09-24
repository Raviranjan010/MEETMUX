from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class RowValidationDetail(BaseModel):
    row_number: int
    flight_number: Optional[str] = None
    error_code: str
    message: str
    field: Optional[str] = None


class IngestionSummary(BaseModel):
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    accepted_flight_ids: List[str] = []
    errors: List[RowValidationDetail] = []


class IngestionResponse(BaseModel):
    status: str
    summary: IngestionSummary
