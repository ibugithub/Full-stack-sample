# {{PROJECT_NAME}} — Quality Requirements (Non-Functional Requirements)

**Version:** 1.0  
**Status:** ⬜ Draft  
**Planning step:** 3 — Quality requirements  
**Standard:** ISO/IEC 25010 product quality model; security requirements reference OWASP ASVS.

> **Guide:** every requirement needs a **measurable target** and a **verification method**. The rows below are common, sensible starting values. Keep, adjust, or delete them; add project-specific ones.

## 1. Quality priorities

| Priority | Characteristic | Why |
|---|---|---|
| 1 | {{e.g. Security and privacy}} | {{REASON}} |
| 2 | {{e.g. Reliability and data integrity}} | {{REASON}} |
| 3 | {{e.g. Usability}} | {{REASON}} |

## 2. Security (QR-SEC)

| ID | Requirement | Target / rule | Verification |
|---|---|---|---|
| QR-SEC-001 | Verification baseline | OWASP ASVS Level 1 overall; Level 2 for authentication, sessions, and access control | Checklist review before release |
| QR-SEC-002 | Transport security | HTTPS only; HSTS enabled | Automated header check |
| QR-SEC-003 | Credential storage | No tokens in readable browser storage or plain device storage | Code review, inspection test |
| QR-SEC-004 | Server-side authorization | Every endpoint that touches user data checks ownership on the server | Automated isolation tests |
| QR-SEC-005 | Rate limiting | Limits on sign-in, sign-up, and password reset | Tests |
| QR-SEC-006 | Logging hygiene | No passwords, tokens, or personal data in logs | Log review |
| QR-SEC-007 | Secrets | Secrets only in environment variables or secret stores; none in Git | Secret scanning in CI |
| QR-SEC-008 | Dependencies | No known critical or high vulnerabilities at release | Dependency audit in CI |

## 3. Privacy (QR-PRV)

| ID | Requirement | Target / rule | Verification |
|---|---|---|---|
| QR-PRV-001 | Data minimization | Collect only data the features need | Inspection |
| QR-PRV-002 | Encryption at rest | Database and backups encrypted at rest | Configuration review |
| QR-PRV-003 | Privacy policy | Public privacy policy describing data use | Inspection |

## 4. Reliability and data integrity (QR-REL)

| ID | Requirement | Target / rule | Verification |
|---|---|---|---|
| QR-REL-001 | No loss of confirmed saves | 0 confirmed saves lost | Tests, incident tracking |
| QR-REL-002 | Integrity constraints | Key rules enforced by database constraints | Constraint tests |
| QR-REL-003 | Backups | {{BACKUP METHOD AND SCHEDULE}} | Job logs |
| QR-REL-004 | Recovery point objective | At most {{e.g. 24 hours}} of data lost in a disaster | Backup schedule |
| QR-REL-005 | Recovery time objective | Service restored within {{e.g. 24 hours}} | Restore drill |
| QR-REL-006 | Restore test | Full restore tested {{e.g. monthly and before each release}} | Drill record |
| QR-REL-007 | Availability | {{e.g. 99.5% monthly}} | Uptime monitor |

## 5. Usability and accessibility (QR-USE)

| ID | Requirement | Target / rule | Verification |
|---|---|---|---|
| QR-USE-001 | Core task speed | {{e.g. main action in at most 4 interactions}} | Usability test |
| QR-USE-002 | Responsive layout | Usable from 360 px to 1920 px wide | Visual tests |
| QR-USE-003 | Accessibility | WCAG 2.1 Level AA | Automated checks plus manual keyboard test |
| QR-USE-004 | Clear messages | Every error says what went wrong and how to fix it | Review |

## 6. Performance efficiency (QR-PERF)

| ID | Requirement | Target | Verification |
|---|---|---|---|
| QR-PERF-001 | API response time | 95% of requests within {{e.g. 500 ms}} at {{DATA VOLUME}} | Load test |
| QR-PERF-002 | Page load | First meaningful screen within {{e.g. 3 s}} on a fast 4G phone connection | Lighthouse |
| QR-PERF-003 | Interaction feedback | Feedback within 100 ms for every action | Manual test |

## 7. Maintainability (QR-MNT)

| ID | Requirement | Target / rule | Verification |
|---|---|---|---|
| QR-MNT-001 | Module boundaries | Code follows the architecture's module structure | Code review |
| QR-MNT-002 | Automated tests | {{e.g. 90% coverage for domain logic, 80% overall}}; every FR has a test | Coverage report |
| QR-MNT-003 | Quality gates | Lint, format, and type checks pass | CI |
| QR-MNT-004 | API contract | Implementation matches the OpenAPI contract | CI |

## 8. Compatibility and portability (QR-CMP)

| ID | Requirement | Target / rule | Verification |
|---|---|---|---|
| QR-CMP-001 | Browsers | {{e.g. latest two versions of Chrome, Edge, Firefox, Safari}} | Cross-browser test |
| QR-CMP-002 | API versioning | Endpoints under `/api/v1/`; breaking changes need a new version | API review |

## 9. Observability (QR-OBS)

| ID | Requirement | Target / rule | Verification |
|---|---|---|---|
| QR-OBS-001 | Structured logs | Time, level, request ID, endpoint, status, duration | Inspection |
| QR-OBS-002 | Error tracking | Unhandled errors reported with personal data removed | Test error |
| QR-OBS-003 | Health check | Endpoint reporting application and database status | Test |

## Change history

- **v1.0 ({{DATE}}):** First version.
