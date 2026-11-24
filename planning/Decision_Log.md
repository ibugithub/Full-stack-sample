# {{PROJECT_NAME}} — Decision Log

**Last updated:** {{DATE}}  
**Purpose:** One register of every product decision. Detailed behavior lives in the owning document named in each entry. Technical decisions are recorded as ADRs in `Design/Architecture/ADR/`.

**Statuses**

- **Confirmed:** explicitly agreed by the owner.
- **Proposed:** a recommended standard default used in drafts; not final until the owner confirms it.
- **Superseded / Replaced:** replaced by a later decision. The entry stays for history, marked with the ID that replaces it.

> **Guide:** add a D- entry the moment the owner decides something. Never delete an entry; mark it superseded instead.

## 1. Confirmed decisions

| ID | Date | Decision | Owning document |
|---|---|---|---|
| D-01 | {{DATE}} | {{PRODUCT TYPE AND INITIAL FOCUS}} | Project Definition |

## 2. Detailed decision sets

> **Guide:** when one decision has many parts (for example, account-switching behavior), list the parts here and refer to them from the table above.

## 3. Proposed defaults

> **Guide:** while drafting, record routine choices as proposals instead of stopping for each one. Review them with the owner in small groups, then mark this section "confirmed in review" with the date and any changes.

| ID | Proposal | Reason | Affects |
|---|---|---|---|
| P-01 | {{STANDARD DEFAULT, e.g. "Timestamps stored in UTC"}} | {{WHY IT IS THE STANDARD CHOICE}} | {{DOCUMENTS}} |

## 4. Open questions (not yet decided)

- {{QUESTION THAT IS DELIBERATELY LEFT FOR LATER}}
