```markdown
# AI Insight Examples (Non-Authoritative)

This document shows example outputs produced by AI systems consuming the engine's event stream.

These insights are **explanatory only** and do not affect system state.

---

## Insight: Capacity Risk Warning

**Summary**
Site Alpha is projected to exceed accommodation capacity within 36 hours.

**Signals**
- 92% capacity reached
- 14 bookings scheduled in next 24h
- Historical no-show rate below threshold

**Recommendation**
Consider delaying non-critical bookings or reallocating to Site Beta.

---

## Insight: FIFO Fairness Alert

**Summary**
FIFO fairness degradation detected.

**Details**
- Crew group B has waited 2.3× longer than historical average
- Priority overrides applied 4 times in last 12 hours

**Recommendation**
Review priority weights for role = "maintenance"

---

## Insight: Incident Reconstruction

**Event Window**
2026-02-01 14:22 → 2026-02-01 16:05

**Findings**
- Booking rejected due to capacity rule
- Manual override not permitted by lifecycle
- No unsafe state entered

**Conclusion**
System operated within defined constraints.

---

## Important Note

These outputs:
- Are generated outside the engine
- Are derived from immutable facts
- Can be regenerated at any time
- Do not influence decisions