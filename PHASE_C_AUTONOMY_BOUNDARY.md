# Phase C Autonomy Boundary

## Purpose

This document defines the strict boundaries under which autonomous actions
may be considered in future phases of the system.

At present, the system operates in advisory mode only.

No autonomous execution is enabled by default.

---

## Current State (Phase A & B)

The system currently supports:

- Deterministic operational enforcement by the core engine
- Immutable event generation
- AI-based interpretation and explanation
- AI-based risk detection
- AI-generated non-binding recommendations
- Human or external-system approval recording

The system does NOT support:

- Autonomous execution
- Automatic state mutation
- AI-driven overrides
- Silent optimisation

---

## Definition of Phase C Autonomy

Phase C autonomy refers to the controlled execution of **pre-approved actions**
under strictly defined conditions.

Autonomy, if enabled, is:

- Explicitly configured
- Narrowly scoped
- Fully auditable
- Reversible
- Contractually agreed

---

## Non-Negotiable Constraints

The following constraints apply to any Phase C autonomy:

1. **No AI Direct Writes**
  AI systems may never write directly to the core engine database.

2. **Pre-Approved Action Types Only**
  Only explicitly whitelisted actions may be executed autonomously.

3. **Human Accountability**
  All autonomous actions must be traceable to a human or organisational approval.

4. **Deterministic Execution**
  Execution paths must be deterministic and replayable.

5. **Full Audit Trail**
  Every autonomous action must produce immutable audit records.

6. **Immediate Kill Switch**
  Autonomy must be disableable instantly without system downtime.

---

## Examples of Permitted Autonomous Actions (Illustrative)

The following are examples only