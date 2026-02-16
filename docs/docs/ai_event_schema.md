# AI Event Schema (Read-Only)

AI systems consume a read-only stream of immutable domain events.

These events represent **facts**, not intentions or UI actions.

---

## Core Event Envelope

Every event emitted by the engine conforms to:

```json
{
 "event_id": "uuid",
 "event_type": "string",
 "occurred_at": "ISO-8601 timestamp",
 "aggregate_type": "booking",
 "aggregate_id": "uuid",
 "payload": { }
}