# DOMAIN_MODEL.md

## Core entities and relationships (see DATABASE.md for full schema)
`Airport 1—* Terminal 1—* Gate`; `Airport 1—* Runway`; `Airport 1—* Flight`; `Flight *—1 Aircraft`; `Flight *—0..1 Gate` (via `gate_assignments`, historized); `Flight 1—* Prediction`; `OptimizationRun 1—* GateAssignment`; `Scenario 1—* CascadeEvent`; `Flight 1—* Alert`; every mutating action → `AuditRecord`.

## Key domain rules
- A **Flight** has both a scheduled and (once known) actual arrival/departure time; delay concepts are always "actual minus scheduled" or "predicted minus scheduled" — never conflated.
- A **Gate** can only ever be in one state at a time: `AVAILABLE | OCCUPIED | RESERVED | BLOCKED | CONFLICT`. `CONFLICT` is a derived/display state set by the conflict engine, not stored as the gate's persistent state — see GATE_SYSTEM.md.
- A **GateAssignment** belongs to exactly one `OptimizationRun` (or the sentinel baseline run) and has a lifecycle `BASELINE → PROPOSED → COMMITTED | REJECTED`.
- A **CascadeEvent** always has a root cause referencing a specific `flight_id` or `gate_id`/`runway_id`, never a free-text-only cause.
- **Domestic vs International** is a property of the Flight (route type), and gate eligibility is a property of the Gate; a valid assignment requires flight.route_type to be in gate.eligible_route_types.

## Glossary
| Term | Definition |
|---|---|
| Taxi time | Minutes between runway touchdown/pushback and gate arrival/departure |
| Turnaround | Minimum ground time a gate must hold a flight between arrival and next departure at that gate |
| Remote stand | A gate/stand without a jetbridge, requiring bus transfer |
| Cascade | A chain of downstream effects triggered by one delay/conflict/closure |
| Committed schedule | The set of `COMMITTED` gate assignments the airport is currently operating against |
