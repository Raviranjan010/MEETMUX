# Rule: Security
- No secret ever committed; `.env.example` documents every key with a placeholder, `.env` is gitignored.
- Every upload is size- and schema-validated before touching the DB.
- Error responses never leak stack traces, DB connection strings, or credentials.
- CORS allow-list is explicit, never `*`.
