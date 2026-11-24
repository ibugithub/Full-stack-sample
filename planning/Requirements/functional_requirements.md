# {{PROJECT_NAME}} — Functional Requirements

**Version:** 1.0  
**Status:** ⬜ Draft  
**Scope:** {{RELEASE SCOPE}}  
**Standard:** ISO/IEC/IEEE 29148 (verifiable, uniquely identified, traceable requirements)  
**Inputs:** Project Definition, Actors, Features, Use Cases, Decision Log

## 1. Introduction

### 1.1 Purpose

This document defines the observable behavior the release must provide. It says **what** the system does, not how it is built. Quality requirements are in `quality_requirements.md`.

### 1.2 Writing rules

1. Every requirement has a stable, unique ID that is never reused.
2. Each requirement states one obligation and is verifiable by test, inspection, or demonstration.
3. **Shall** means mandatory. **Should** means recommended. **May** means allowed.
4. Each requirement traces to a use case, feature, or decision.
5. Requirements that depend on a proposed default cite its P- ID.
6. No silent assumptions: unresolved details become open questions or proposals.

### 1.3 Record format

```
### FR-AREA-001 — Short title

- **Statement:** The application shall …
- **Acceptance criteria:**
  1. Observable condition that proves it.
- **Trace:** UC-xx, D-xx · **Status:** Draft
```

### 1.4 ID prefixes

> **Guide:** one prefix per area. Common ones are listed; adapt them.

| Prefix | Area |
|---|---|
| FR-SYS | System-wide behavior (saving, validation, loading and error states) |
| FR-ACC | Accounts, authentication, settings, administration |
| FR-{{AREA}} | {{AREA}} |
| FR-INT | Cross-cutting data integrity |

### 1.5 Terms

- {{TERM}}: {{MEANING}}

---

## 2. System-wide requirements (FR-SYS)

> **Guide:** these are useful in almost every project. Keep, adapt, or remove.

### FR-SYS-001 — Confirmed persistence

- **Statement:** The application shall report a save as successful only after the data has been stored. If storing fails, it shall keep the entered data and say that the save failed.
- **Acceptance criteria:**
  1. A failed save shows no success message and keeps the entered data.
  2. A failed save leaves no partially stored data.
- **Trace:** {{UC}} · **Status:** Draft

### FR-SYS-002 — No duplicate submissions

- **Statement:** While a save is in progress, repeated activations of the same save action shall not start another save.
- **Trace:** {{UC}} · **Status:** Draft

### FR-SYS-003 — Server-side validation with field messages

- **Statement:** The server shall validate every rule for every write and reject invalid input as a whole, naming each invalid field.
- **Trace:** {{UC}} · **Status:** Draft

### FR-SYS-004 — Loading, empty, and error states

- **Statement:** Every screen that loads data shall show distinct loading, empty, and error states, with a retry action for errors.
- **Trace:** {{UC}} · **Status:** Draft

## 3. Accounts (FR-ACC)

> **Guide:** typical requirements: data ownership, server-side authorization, registration, verification, sign-in methods, password reset and change, profile, settings, session lifetime, operator access boundary, disabling accounts, legal pages.

### FR-ACC-001 — {{TITLE}}

- **Statement:** {{STATEMENT}}
- **Acceptance criteria:**
  1. {{CRITERION}}
- **Trace:** {{UC}} · **Status:** Draft

## 4. {{AREA}} (FR-{{AREA}})

### FR-{{AREA}}-001 — {{TITLE}}

- **Statement:** {{STATEMENT}}
- **Acceptance criteria:**
  1. {{CRITERION}}
- **Trace:** {{UC}} · **Status:** Draft

## {{N}}. Cross-cutting data integrity (FR-INT)

### FR-INT-001 — Enforcement below the interface

- **Statement:** Ownership and integrity rules shall be enforced by the backend, and by database constraints where possible. The user interface alone is never sufficient.
- **Trace:** All · **Status:** Draft

### FR-INT-002 — Atomic operations

- **Statement:** Every operation that changes more than one stored item shall either complete fully or change nothing.
- **Trace:** FR-SYS-001 · **Status:** Draft

---

## {{N}}. Traceability matrix

| Use case | Requirements |
|---|---|
| UC-01 {{NAME}} | {{FR IDs}} |

## {{N}}. Status summary

| Area | Count | Status |
|---|---|---|
| All requirements | {{N}} | Draft |

## Change history

- **v1.0 ({{DATE}}):** First version.
