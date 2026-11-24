# {{PROJECT_NAME}} — Requirements Engineering: Actors / Users

**Version:** 1.0  
**Status:** ⬜ Draft  
**Scope:** {{RELEASE SCOPE}}

## 1. Purpose

Define the human and external actors that interact with {{PROJECT_NAME}} and the boundaries of their responsibilities.

> **Guide:** an actor is anyone or anything outside the system that interacts with it. Common actors to consider: visitor (not signed in), signed-in user, administrator or operator, identity providers, email service, payment provider, other external systems.

## 2. Actor summary

| ID | Actor | Type | Summary |
|---|---|---|---|
| ACT-00 | {{e.g. Visitor}} | Human | {{SHORT DESCRIPTION}} |
| ACT-01 | {{e.g. User}} | Human | {{SHORT DESCRIPTION}} |
| ACT-02 | {{e.g. Identity provider}} | External service | {{SHORT DESCRIPTION}} |

## 3. Human actors

### ACT-01: {{ACTOR NAME}}

- **Type:** Human
- **Role:** {{ROLE}}
- **Primary responsibility:** {{RESPONSIBILITY}}
- **Access boundary:** {{WHAT THEY CAN AND CANNOT SEE OR CHANGE}}

## 4. Goals of the main actor

1. {{GOAL}}

## 5. Responsibilities of the main actor

- {{RESPONSIBILITY}}

## 6. External actors

### ACT-02: {{EXTERNAL ACTOR}}

- **Type:** External service
- **Role:** {{ROLE}}
- **Responsibility:** {{RESPONSIBILITY}}
- **Data it receives:** {{DATA, and what it never receives}}

## 7. Interaction model

- **Clients:** {{CLIENTS}}
- **Operating model:** {{ONLINE / OFFLINE}}
- **Account model:** {{ACCOUNT MODEL}}
- **Authorization:** {{WHERE ACCESS IS ENFORCED}}

## 8. Roles and capabilities excluded from V1

- {{EXCLUDED ROLE}}

## 9. Completion criteria

This document is complete when:

- Every human and external actor of V1 is identified.
- Each actor's access boundary is explicit.
- Excluded roles are listed.
- The owner has confirmed it.

## Change history

- **v1.0 ({{DATE}}):** First version.
