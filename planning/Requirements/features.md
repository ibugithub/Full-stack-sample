# {{PROJECT_NAME}} — Requirements Engineering: Features / Capabilities

**Version:** 1.0  
**Status:** ⬜ Draft  
**Scope:** {{RELEASE SCOPE}}

## 1. Purpose

Define the capabilities the product must provide in V1. This document says **what** the product does. Detailed rules, validation, and verification belong in the functional and quality requirements.

## 2. Feature overview

> **Guide:** a numbered list of every capability. Each one gets its own section below.

1. {{CAPABILITY}}

## 2A. Accounts and authentication

> **Guide:** keep or remove. Most products need sign-up, sign-in methods, password recovery, sign-out, profile, settings, and legal pages.

- {{ACCOUNT CAPABILITY}}

## 2B. Clients and platform behavior

> **Guide:** if there is more than one client, state the parity rule (same features on every client or not) and list platform-specific capabilities.

- {{CLIENT RULE}}

## 3. {{CAPABILITY NAME}}

**Purpose:** {{WHY IT EXISTS}}

The user must be able to:

- {{ABILITY}}

> **Guide:** repeat a section like this for each capability: purpose, abilities, key rules. Typical areas: core records (create, view, edit, delete), organization (categories, tags), history and search, filters and sorting, analytics or reports, dashboard, deleted-item recovery, notifications.

## {{N}}. Cross-cutting rules

> **Guide:** rules that apply across all capabilities, for example "every record belongs to exactly one account" or "deleting never removes data permanently".

1. {{RULE}}

## {{N}}. Out of scope for V1

- {{EXCLUDED CAPABILITY}}

## {{N}}. Where remaining details are resolved

| Detail | Resolved in |
|---|---|
| Field rules and validation | Functional Requirements |
| Security, performance, backup, privacy | Quality Requirements |
| Screen layout | UX Design |

## Change history

- **v1.0 ({{DATE}}):** First version.
