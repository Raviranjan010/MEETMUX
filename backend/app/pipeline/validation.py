from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set
from sqlalchemy.orm import Session
from app.models import Aircraft, Flight
from app.models.enums import RouteType

REQUIRED_FIELDS = [
    "flight_number",
    "airline",
    "aircraft_type_code",
    "route_type",
    "origin",
    "destination",
    "scheduled_arrival",
    "scheduled_departure",
]


class ValidationErrorItem:
    def __init__(self, row_number: int, error_code: str, message: str, field: Optional[str] = None, flight_number: Optional[str] = None):
        self.row_number = row_number
        self.error_code = error_code
        self.message = message
        self.field = field
        self.flight_number = flight_number

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row_number": self.row_number,
            "flight_number": self.flight_number,
            "error_code": self.error_code,
            "message": self.message,
            "field": self.field,
        }


def parse_datetime(dt_str: Any) -> Optional[datetime]:
    if isinstance(dt_str, datetime):
        if dt_str.tzinfo is None:
            return dt_str.replace(tzinfo=timezone.utc)
        return dt_str.astimezone(timezone.utc)

    if not isinstance(dt_str, str):
        return None

    try:
        # Support ISO8601 parsing with Z or timezone offsets
        clean_str = dt_str.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def validate_flight_batch(
    raw_rows: List[Dict[str, Any]],
    db: Session,
) -> Tuple[List[Dict[str, Any]], List[ValidationErrorItem]]:
    """
    Validates a list of raw flight row dictionaries per docs/DATA_DICTIONARY.md.
    Returns (accepted_rows, validation_errors).
    """
    accepted: List[Dict[str, Any]] = []
    errors: List[ValidationErrorItem] = []

    # Cache existing aircraft type codes
    valid_aircraft_types = {
        ac.type_code for ac in db.query(Aircraft.type_code).distinct()
    }

    # Track seen (flight_number, arrival_dt) within this batch and DB to catch duplicates
    seen_in_batch: Set[Tuple[str, datetime]] = set()

    for row_idx, row in enumerate(raw_rows, start=1):
        flight_num = str(row.get("flight_number", "")).strip() if row.get("flight_number") is not None else None

        # 1. Check Missing Required Fields
        missing = [f for f in REQUIRED_FIELDS if f not in row or row[f] is None or str(row[f]).strip() == ""]
        if missing:
            errors.append(
                ValidationErrorItem(
                    row_number=row_idx,
                    flight_number=flight_num,
                    error_code="MISSING_REQUIRED_FIELD",
                    message=f"Missing required field(s): {', '.join(missing)}",
                    field=missing[0],
                )
            )
            continue

        # 2. Check Route Type Enum
        route_str = str(row["route_type"]).strip().upper()
        if route_str not in [RouteType.DOMESTIC.value, RouteType.INTERNATIONAL.value]:
            errors.append(
                ValidationErrorItem(
                    row_number=row_idx,
                    flight_number=flight_num,
                    error_code="MALFORMED_ROW",
                    message=f"Invalid route_type '{row['route_type']}'. Must be DOMESTIC or INTERNATIONAL.",
                    field="route_type",
                )
            )
            continue

        # 3. Check Timestamps
        arr_dt = parse_datetime(row["scheduled_arrival"])
        if arr_dt is None:
            errors.append(
                ValidationErrorItem(
                    row_number=row_idx,
                    flight_number=flight_num,
                    error_code="MALFORMED_ROW",
                    message=f"Invalid scheduled_arrival timestamp format: '{row['scheduled_arrival']}'",
                    field="scheduled_arrival",
                )
            )
            continue

        dep_dt = parse_datetime(row["scheduled_departure"])
        if dep_dt is None:
            errors.append(
                ValidationErrorItem(
                    row_number=row_idx,
                    flight_number=flight_num,
                    error_code="MALFORMED_ROW",
                    message=f"Invalid scheduled_departure timestamp format: '{row['scheduled_departure']}'",
                    field="scheduled_departure",
                )
            )
            continue

        # 4. Check Timestamp Order (departure must be > arrival)
        if dep_dt <= arr_dt:
            errors.append(
                ValidationErrorItem(
                    row_number=row_idx,
                    flight_number=flight_num,
                    error_code="INVALID_TIMESTAMP_ORDER",
                    message=f"scheduled_departure ({dep_dt.isoformat()}) must be later than scheduled_arrival ({arr_dt.isoformat()})",
                    field="scheduled_departure",
                )
            )
            continue

        # 5. Check Unknown Aircraft Type
        ac_type = str(row["aircraft_type_code"]).strip()
        if ac_type not in valid_aircraft_types:
            errors.append(
                ValidationErrorItem(
                    row_number=row_idx,
                    flight_number=flight_num,
                    error_code="UNKNOWN_AIRCRAFT_TYPE",
                    message=f"Unknown aircraft type code '{ac_type}'. Must match a registered aircraft type.",
                    field="aircraft_type_code",
                )
            )
            continue

        # 6. Check Duplicates (within current batch)
        flight_key = (flight_num, arr_dt)
        if flight_key in seen_in_batch:
            errors.append(
                ValidationErrorItem(
                    row_number=row_idx,
                    flight_number=flight_num,
                    error_code="DUPLICATE_FLIGHT",
                    message=f"Duplicate flight_number '{flight_num}' with arrival '{arr_dt.isoformat()}' in batch",
                    field="flight_number",
                )
            )
            continue

        # 7. Check Duplicates (against database)
        existing = db.query(Flight).filter(
            Flight.flight_number == flight_num,
            Flight.scheduled_arrival == arr_dt,
        ).first()
        if existing:
            errors.append(
                ValidationErrorItem(
                    row_number=row_idx,
                    flight_number=flight_num,
                    error_code="DUPLICATE_FLIGHT",
                    message=f"Flight '{flight_num}' with scheduled_arrival '{arr_dt.isoformat()}' already exists in database",
                    field="flight_number",
                )
            )
            continue

        seen_in_batch.add(flight_key)
        
        # Validated row ready for cleaning
        validated_row = dict(row)
        validated_row["flight_number"] = flight_num
        validated_row["airline"] = str(row["airline"]).strip().upper()
        validated_row["aircraft_type_code"] = ac_type
        validated_row["route_type"] = RouteType(route_str)
        validated_row["origin"] = str(row["origin"]).strip().upper()
        validated_row["destination"] = str(row["destination"]).strip().upper()
        validated_row["scheduled_arrival"] = arr_dt
        validated_row["scheduled_departure"] = dep_dt
        if "runway_code" in row and row["runway_code"]:
            validated_row["runway_code"] = str(row["runway_code"]).strip().upper()

        accepted.append(validated_row)

    return accepted, errors
