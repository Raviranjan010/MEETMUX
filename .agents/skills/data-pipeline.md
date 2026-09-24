# Skill: data-pipeline

**Purpose:** Ingest, validate, clean, and normalize flight/weather CSV or JSON data into the database.
**When to use:** Phase 3, and any later re-upload of demo/live data.
**Inputs:** Raw CSV/JSON file matching docs/DATA_DICTIONARY.md field list.
**Outputs:** Persisted flight/weather_records rows; a per-row validation report (accepted/rejected with reason codes).
**Files involved:** backend/app/pipeline/validation.py, cleaning.py, ingestion.py; tests/pipeline/
**Validation requirements:** Every required field present and typed correctly; no duplicate flight_number+scheduled_arrival; departure > arrival; aircraft type resolvable.
**Failure handling:** Reject the specific row with a named error code (docs/DATA_DICTIONARY.md); never drop rows silently or accept malformed data 'to keep the demo working'.
**Prohibited shortcuts:** Do not skip validation for 'trusted' demo data; do not auto-correct malformed timestamps by guessing.
