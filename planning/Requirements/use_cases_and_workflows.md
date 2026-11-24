# {{PROJECT_NAME}} — Requirements Engineering: Use Cases / Workflows

**Version:** 1.0  
**Status:** ⬜ Draft  
**Scope:** {{RELEASE SCOPE}}  
**Actors:** see `users.md`

> **Guide:** a use case describes how an actor reaches a goal, step by step. Cover every actor goal in `users.md` and every capability in `features.md`. IDs are stable: never renumber, only add.

## Use case index

| ID | Name | Primary actor |
|---|---|---|
| UC-01 | {{USE CASE}} | {{ACTOR}} |

**Common precondition:** {{e.g. the user is signed in}}

---

## UC-01 — {{USE CASE NAME}}

**Primary actor:** {{ACTOR}}  
**Trigger:** {{WHAT STARTS IT}}  
**Preconditions:** {{WHAT MUST BE TRUE BEFORE}}

### Main flow

1. {{STEP}}
2. {{STEP}}

### Alternative flows

- **{{CONDITION}}:** {{WHAT HAPPENS}}

### Postcondition

{{WHAT IS TRUE AFTERWARDS}}

> **Guide:** repeat for each use case. Typical ones: create, view, edit, delete, restore, search and filter, sort, analyze, sign up, sign in, recover password, manage settings, administer accounts.

---

## Cross-workflow rules

1. {{RULE THAT APPLIES TO EVERY WORKFLOW}}

## Completion criteria

Complete when every actor goal and every feature is covered by a use case, all confirmed decisions are reflected, and the owner has confirmed it.

## Change history

- **v1.0 ({{DATE}}):** First version.
