```markdown
# Engine Guarantees

## Determinism
Identical inputs always produce identical outcomes.

## Lifecycle Integrity
Invalid state transitions are impossible.

## Audit Immutability
Audit records are append-only and never modified.

## Capacity Safety
Hard capacity limits prevent over-allocation.

## Event Truth
Events reflect domain facts, not UI actions.

## AI Boundary (Non-Authoritative Intelligence)

This engine enforces a strict separation between **operational authority** and **artificial intelligence**.

### AI Capabilities
AI systems MAY:
- Observe immutable domain events
- Analyze historical and real-time event streams
- Generate explanations, summaries, and forecasts
- Propose configuration changes (non-binding)
- Produce compliance, safety, and audit reports

### AI Restrictions
AI systems MUST NOT:
- Create or modify bookings
- Change lifecycle states
- Override capacity or FIFO constraints
- Write directly to the database
- Mutate operational state in any form

### Authority Guarantee
All operational decisions are:
- Deterministic
- Rule-driven
- Human-approved
- Replayable from event history

AI output is advisory only and carries no execution authority.

This boundary is enforced by architecture, not policy.