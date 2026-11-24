# {{PROJECT_NAME}} — API Design

**Version:** 1.0  
**Status:** ⬜ Draft  
**Planning step:** 8 — API design  
**Contract:** [`openapi.yaml`](openapi.yaml) (OpenAPI 3.1). This document explains conventions; the YAML file is the exact contract.

## 1. Conventions

> **Guide:** common REST defaults; adjust as needed.

| Topic | Rule |
|---|---|
| Base path | `/api/v1/` |
| Format | JSON, UTF-8, `snake_case` field names |
| Authentication | {{e.g. Authorization: Bearer access token}} |
| IDs | {{e.g. integers}} |
| Timestamps | ISO 8601, UTC in responses |
| Money | Decimal strings, never JSON numbers |
| Partial updates | `PATCH` with changed fields plus the `version` that was read |
| Ownership | The user always comes from the token; another user's object returns 404 |

## 2. Pagination

{{e.g. cursor pagination: ?limit=&cursor=; response has results, next_cursor, and a summary of the full matching set}}

## 3. Filtering and sorting

| Parameter | Meaning |
|---|---|
| `{{param}}` | {{MEANING}} |

## 4. Error format

```json
{
  "detail": "Readable message.",
  "code": "machine_readable_code",
  "errors": {"field": ["Message for this field."]}
}
```

| HTTP | `code` | When |
|---|---|---|
| 400 | `validation_error` | Field rules failed |
| 401 | `not_authenticated` | Missing or invalid credentials |
| 403 | `permission_denied` | Not allowed |
| 404 | `not_found` | Missing, or owned by another user |
| 409 | `version_conflict` | Changed since it was read |
| 429 | `throttled` | Rate limit; includes `retry_after` |
| 500 | `server_error` | Unexpected; includes `request_id` |

## 5. Endpoints

> **Guide:** one table per area. Every endpoint names the requirements it serves.

### 5.1 {{AREA}}

| Method and path | Purpose | Requirements |
|---|---|---|
| `GET /{{resource}}` | {{PURPOSE}} | {{FR IDs}} |

## 6. Rate limits

{{LIMITS PER ENDPOINT GROUP}}

## 7. Compatibility rules

- Adding optional fields is allowed in v1.
- Removing or renaming fields, or changing types or meaning, requires `/api/v2/`.
- Clients ignore unknown response fields.

## Change history

- **v1.0 ({{DATE}}):** First version.
