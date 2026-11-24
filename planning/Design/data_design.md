# {{PROJECT_NAME}} — Data Design

**Version:** 1.0  
**Status:** ⬜ Draft  
**Planning step:** 7 — Data design  
**Database:** {{DATABASE AND VERSION}}  
**Inputs:** Domain Model, ADRs

## 1. Entity-relationship diagram

```mermaid
erDiagram
  {{table_a}} ||--o{ {{table_b}} : owns
  {{table_a}} {
    bigint id PK
  }
```

## 2. Conventions

> **Guide:** common defaults; adjust to the project.

| Item | Convention |
|---|---|
| Primary keys | {{e.g. bigint identity}} |
| Timestamps | {{e.g. timestamptz in UTC; created_at and updated_at on every table}} |
| Optimistic locking | {{e.g. version integer incremented on every update}} |
| Soft delete | {{e.g. deleted_at nullable timestamp}} |
| Money | {{e.g. NUMERIC with currency code; never floating point}} |
| Enumerations | {{e.g. varchar with CHECK constraint}} |

## 3. Tables

### 3.1 `{{table}}`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | {{TYPE}} | PK | |
| `{{column}}` | {{TYPE}} | {{CONSTRAINTS}} | {{NOTES}} |

| Constraint or index | Definition | Purpose |
|---|---|---|
| `{{name}}` | {{DEFINITION}} | {{INVARIANT OR QUERY IT SUPPORTS}} |

## 4. Key queries

| Query | Approach |
|---|---|
| {{QUERY}} | {{HOW IT IS BUILT AND WHICH INDEX IT USES}} |

## 5. Data volume

{{EXPECTED ROWS PER USER AND IN TOTAL; THE VOLUME USED FOR PERFORMANCE TARGETS}}

## 6. Migration plan

| Order | Module | Migration |
|---|---|---|
| 1 | {{MODULE}} | {{CHANGE}} |

Rules: every migration is reversible or documents why not; migrations already released are never edited; production migrations run only after a fresh backup.

## 7. Backup, restore, and retention

> **Guide:** how data is backed up, where backups live, how a restore works and is tested, and how long data and backups are kept. Personal data must never be stored in the code repository.

## Change history

- **v1.0 ({{DATE}}):** First version.
