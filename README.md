# Operational Workflow Engine

## What This Is

This repository contains a **self-hosted, status-driven operational workflow engine**
designed for **safety-critical environments**.

It enforces:
- Explicit lifecycle states
- Deterministic transitions
- Hard capacity constraints
- Immutable audit logs
- First-class event emission

It is **not** a SaaS product and **not** an end-user application.

---

## Who This Is For

- Enterprise operations teams
- Systems integrators
- Government platforms
- OEM vendors embedding workflow logic

---

## Core Guarantees

- No silent state changes
- No invalid transitions
- No overbooking
- No deleted history
- No AI autonomy

Every action is:
- validated
- audited
- timestamped
- attributable

---

## Architecture Overview

- `models.py` → persistence
- `domain/` → business authority
- `events/webhooks` → external truth
- `config.py` → environment contracts

All state changes pass through domain logic.

---

## Deployment Model

- Self-hosted
- API-first
- Database-backed
- Event-driven

The same build runs across:
- mining
- oil & gas
- construction
- energy
- government

---

## What This Is Not

- Not a rostering system
- Not a payroll system
- Not a UI product
- Not autonomous AI

---

## Licensing

See `LICENSE.md`.