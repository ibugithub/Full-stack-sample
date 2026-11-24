# {{PROJECT_NAME}} — UX Design

**Version:** 1.0  
**Status:** ⬜ Draft  
**Planning step:** 5 — UX design  
**Contents:** principles, navigation, screen inventory, key flows, low-fidelity wireframes, interaction rules, visual foundations, and per-platform notes.

## 1. UX principles

> **Guide:** 4 to 6 principles specific to this product, for example "the main action is always one tap away".

1. {{PRINCIPLE}}

## 2. Navigation

```mermaid
flowchart TD
  Home[{{Home}}] --> A[{{Area}}]
```

| Width | Primary navigation |
|---|---|
| Below 768 px | {{e.g. bottom bar}} |
| 768 px and wider | {{e.g. sidebar}} |

## 3. Screen inventory

> **Guide:** every screen and dialog, with its address, who can open it, and the requirements it serves.

| ID | Screen | Address | Access | Requirements |
|---|---|---|---|---|
| S-01 | {{SCREEN}} | `{{/path/}}` | {{Public / Signed in}} | {{FR IDs}} |
| D-01 | {{DIALOG}} | {{Dialog / Panel}} | {{ACCESS}} | {{FR IDs}} |

## 4. Key flows

```mermaid
flowchart LR
  A[{{Start}}] --> B[{{Step}}] --> C[{{Result}}]
```

## 5. Wireframes (low fidelity)

> **Guide:** simple text sketches of the main screens at phone width. Use sample data with neutral names, never real people.

```
┌────────────────────────────────┐
│ {{APP NAME}}           (◉ User)│
├────────────────────────────────┤
│ {{CONTENT}}                    │
└────────────────────────────────┘
```

## 6. Interaction rules

| Topic | Rule |
|---|---|
| Saving | {{e.g. button disabled with spinner while saving; toast on success}} |
| Errors | {{e.g. field errors under the field; banner with Retry for server errors}} |
| Empty states | {{e.g. friendly message plus the main action}} |
| Loading | {{e.g. skeleton rows, never "no data" while loading}} |
| Confirmation | {{e.g. delete names the item and how to undo}} |
| Offline | {{BEHAVIOR}} |

## 7. Visual foundations

| Element | Decision |
|---|---|
| Framework | {{UI FRAMEWORK}} |
| Theme | {{LIGHT / DARK}} |
| Colors | {{PALETTE, with 4.5:1 text contrast}} |
| Typography | {{FONTS AND SIZES}} |
| Icons | {{ICON SET}} |

## 8. Validation before build

- {{e.g. click through the wireframes with three users}}

## 9. Platform-specific notes

> **Guide:** one subsection per additional client, such as a mobile app: navigation, screen differences, notifications, platform-only states.

## Change history

- **v1.0 ({{DATE}}):** First version.
