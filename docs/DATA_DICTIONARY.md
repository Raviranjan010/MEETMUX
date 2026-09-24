# DATA_DICTIONARY.md

## flight (upload/API shape)
| Field | Type | Required | Notes |
|---|---|---|---|
| flight_number | string(8) | yes | e.g. "AI202" |
| airline | string(4) | yes | IATA-style code |
| aircraft_type_code | string(8) | yes | must resolve to an `aircraft.type_code` |
| route_type | enum DOMESTIC/INTERNATIONAL | yes | |
| origin, destination | string(4) | yes | airport codes |
| scheduled_arrival, scheduled_departure | ISO8601 datetime | yes | departure must be > arrival |
| runway_code | string(8) | no | assigned at scheduling time if provided, else auto-assigned round-robin across active runways |

`scheduled_taxi_minutes`: NOT a per-flight field — it's `runways.taxi_base_minutes`, a static per-runway reference value (e.g. RWY-1 = 12.0 min, RWY-2 = 15.0 min for the demo dataset), used as the zero-delay baseline per REQUIREMENTS R7.

## Validation errors (per row, on upload)
`DUPLICATE_FLIGHT` (same flight_number+scheduled_arrival already exists), `INVALID_TIMESTAMP_ORDER` (departure ≤ arrival), `UNKNOWN_AIRCRAFT_TYPE`, `MISSING_REQUIRED_FIELD`, `MALFORMED_ROW` (unparsable CSV line).

## Demo dataset generation (Phase 2 seed)
`scripts/seed_demo.py`, fixed `random.seed(42)`: 2 runways (`RWY-1`, `RWY-2`, `taxi_base_minutes` 12.0/15.0), 30 gates spread across 3 terminals (10 each), mixed JETBRIDGE/REMOTE and SMALL/MEDIUM/LARGE/eligible_route_types to guarantee both feasible and intentionally-tight scenarios exist, 100 flights spread across a representative operating day with a mix of DOMESTIC/INTERNATIONAL, multiple airlines (≥5) and aircraft types (≥4), all `is_synthetic=true`.
