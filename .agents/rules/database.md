# Rule: Database
- Schema matches docs/DATABASE.md field-for-field; any needed addition goes through a DECISION_LOG entry first.
- Every FK has an index; every list-filterable column has an index.
- Alembic migrations are incremental and reversible; never hand-edit the DB schema outside a migration.
- Seed script is idempotent and produces exactly 100 flights / 30 gates / 2 runways.
