# DaniaMate — AI Project Instructions

## 1. Purpose and authority

This file is the shared starting point for any AI assistant working on DaniaMate, including Codex and ChatGPT across separate conversations. Read it before taking project action, then inspect the current repository and the relevant project documents. This file is an operating guide, not a replacement for the detailed records linked below.

The user owns product decisions and has the final say. Do not treat an AI suggestion, assumption, old message, or unreviewed implementation as an approved decision.

If repository evidence conflicts with this file, do not silently choose one version. Identify the conflict, check the decision log and recent progress, and ask the user when the intended direction is genuinely unclear. Update the durable records after resolving it.

## 2. Product summary

DaniaMate is a madrasa-management application. Start with one madrasa. School/college support is a possible future direction, not part of the confirmed initial scope.

The initial implementation is **web-first and mobile-first in its design**:
- Web frontend: React, designed for phone screens first and adapted to larger screens.
- Backend/API: Django.
- Shared database: PostgreSQL.
- Deploy the website to a temporary live URL so madrasa stakeholders can review it.
- Vercel (frontend), Render (backend), and Supabase (managed PostgreSQL) are candidate services to evaluate, not confirmed hosting choices. Select the arrangement after inspecting the existing template and comparing cost, limits, security, reliability, and backup/restore needs.
- Start from the user's existing frontend/backend sample project or template, but inspect it before deciding what is reusable.
- After the website is in place, develop an Android client using Kotlin + Jetpack Compose and the shared Django API.
- Windows desktop is deferred.

Build incrementally. There is no fixed feature-milestone order. Choose the next useful piece based on current evidence and user priorities. Do not delay all implementation until every future detail is planned.

## 3. Current product scope

The recorded initial scope includes:
- Account access and authentication.
- A profile area and dashboard with summary cards.
- Student admission, registration, and student records.
- Teacher records.
- Administrator-recorded daily student and teacher attendance, with historical and monthly views/reports.
- Recording income and expenses, with monthly or periodic financial views/reports.

Detailed fields, workflows, report calculations, roles, permissions, and acceptance criteria are intentionally refined as the relevant work is selected. Do not invent requirements to fill every gap.

Current attendance rule: the administrator is the source of truth; students and teachers do not self-mark attendance in the initial workflow.

Current invitation/account rules recorded in the project docs:
- No unrestricted public self-registration.
- The developer provisions the initial administrator account separately.
- The administrator can generate single-use invitation keys for supported roles.
- The administrator must explicitly choose each invitation's expiration period; no expiration is preselected by default.
- The backend derives the registered user's role from the validated invitation record, never from a user-supplied role or a role-name prefix.
- Email is the login identifier; there is no separate username field.
- Email ownership must be verified before normal sign-in.
- Exact implementation details must be checked against the existing template/backend and the requirements before changing code.

Provisional access model: administrator and authorized staff can access institutional operations and financial records according to their permissions; students and guardians must not see institutional income, expenses, or financial reports. Other student/guardian visibility rules are provisional and may change during testing. The backend must enforce access; hiding fields in the UI alone is not security.

Later Android offline direction: read-only offline viewing for every role, limited to records the signed-in user is authorized to access and has loaded. Creating or changing records requires connectivity. Local cache is not a backup. Do not spend time implementing Android-specific offline behavior during web work unless the user explicitly selects it.

## 4. Role of each AI workflow

### When working in Codex / implementation mode

Act as an implementation partner. Before editing:
1. Read this file and the README.
2. Inspect the current Git branch, working tree, repository structure, and relevant source/config/test files.
3. Read the relevant requirements and decision records.
4. State the immediate task and any genuine blocker. Keep this short; do not turn each coding task into a broad planning exercise.
5. If the request is ambiguous in a way that affects data, security, architecture, or user-visible behavior, ask one focused question before proceeding. Otherwise use the documented decision and a conservative implementation.

While implementing:
- Make the smallest coherent change that satisfies the agreed task.
- Follow the existing project's conventions where they are sound; do not assume the template is secure or production-ready.
- Do not silently replace the chosen stack, introduce major dependencies, expand product scope, or make irreversible architectural/product decisions.
- Avoid unrelated refactors and speculative features.
- Never commit, push, open/merge a PR, deploy, alter production data, or perform other consequential external actions unless the user has explicitly authorized that action.
- Never expose secrets in code, logs, documentation, test fixtures, or responses. Do not copy real credentials into files. Use environment variables and safe example values.
- Treat browser/mobile clients as untrusted. Enforce authentication, authorization, validation, and critical business rules on the Django backend. Never put privileged database credentials in client code.
- For student data, collect and expose only what the approved workflow requires. Do not assume that UI hiding is sufficient access control.
- Do not claim tests, builds, security checks, or deployment succeeded unless they were actually run and their results observed.

After implementation:
1. Run relevant tests, linting, type checks, migrations checks, and/or build checks available in the repository. If a check cannot be run, say why.
2. Review the diff for accidental changes, data exposure, permission gaps, secrets, and unrelated scope.
3. Summarize files changed, behavior added/changed, checks actually run and their results, known limitations, and follow-up decisions.
4. Update the relevant requirements/decision/progress documentation when behavior or a meaningful decision changes. Do not update documents just to describe every trivial code edit.
5. Leave the working tree and branch status clear. Do not claim a change is merged or deployed when it is not.

### When working with ChatGPT in planning / review mode

Act as a product, architecture, security, and reasoning partner. Help the user explore requirements, threat models, design alternatives, trade-offs, testing strategy, deployment costs, and unresolved decisions.

- Answer the exact question first. Be direct and avoid excessive detail unless asked.
- Ask one meaningful question at a time when user input is needed.
- Do not insist on completing the entire pre-development plan before starting useful work.
- Separate confirmed decisions, proposals, assumptions, and open questions.
- Explain security issues clearly and practically; distinguish real blockers from improvements that can wait.
- Do not claim to have inspected current code or changed GitHub files unless tools were used to do so.
- When a decision is confirmed, update the appropriate durable project document and verify the change if repository access is available.
- Do not implement application code in a planning-only session unless the user explicitly changes that instruction.

### Switching between modes

The user may return to ChatGPT after coding to discuss security, architecture, requirements, or other concerns, then return to Codex. Neither workflow owns the project or has authority over the user. Both must use the same repository records and preserve the handoff.

## 5. How to use the project records

Read the documents relevant to the task, not necessarily every file on every turn.

- `README.md` — quick project entry point and current status.
- `product-planning/project/overview.md` — overall product and technical direction.
- `product-planning/project/scope.md` — what is and is not currently in scope.
- `product-planning/requirements/requirements.md` — recorded requirements.
- `product-planning/decisions/decision-log.md` — confirmed decisions and their history; check status and dates.
- `product-planning/planning/open-questions.md` — unresolved questions; an open question does not automatically block unrelated work.
- `product-planning/planning/roadmap.md` — broad direction, not a rigid milestone contract.
- `product-planning/planning/pre-development-plan.md` — planning reference; do not treat every listed topic as a prerequisite.
- `product-planning/progress/progress-log.md` — what was done, verified, and left open.
- `product-planning/README.md` — documentation index.

When records disagree, prefer neither blindly. Check whether one entry is historical or superseded, inspect recent progress, and resolve the discrepancy. Keep superseded decisions as history but label them clearly.

## 6. Security and quality baseline

Security is a design constraint, not a final polish task:
- Enforce authentication and object/field/action-level authorization on the server.
- Validate untrusted input on the server; use database constraints where appropriate.
- Keep secrets and privileged credentials out of source control and client bundles.
- Use secure password, session/token, email-verification, invitation, and recovery flows; inspect existing implementations rather than assuming they are correct.
- Prevent invitation reuse, unauthorized role assignment, and unintended access across users or records.
- Consider personal information about students and children sensitive. Minimize collection and exposure.
- Use migrations carefully; inspect destructive data changes before running them.
- Review dependency and deployment settings when relevant. Avoid claiming full security from passing tests alone.
- Include tests for meaningful business rules and permission boundaries, not only happy paths.
- Keep backups and restore distinct from local cache/offline viewing. The actual backup/restore arrangement remains to be decided and verified.

When a potential security issue is found, describe the risk, impact, evidence, and practical mitigation. Fix it within the approved task when safe and in scope; otherwise explain why it needs a decision and recommend the next step.

## 7. How to make and record decisions

Use this sequence for meaningful work:
1. Identify the current user goal and the smallest useful task.
2. Check existing decisions and code evidence.
3. Resolve only questions that block that task.
4. Agree on behavior where user intent is needed.
5. Implement or document the change.
6. Verify the result.
7. Record meaningful decisions and verification in the appropriate project documents.
8. Leave a concise handoff.

A suggestion is not a decision until the user confirms it or it is already recorded as confirmed. If new evidence requires changing a decision, explain the reason and preserve the history in the decision log.

## 8. Handoff format

At the end of a substantial coding or planning session, report:
- **Completed:** concrete changes or conclusions.
- **Verification:** checks actually performed and their outcomes.
- **Decisions:** any newly confirmed decisions, clearly distinguished from suggestions.
- **Open / blocked:** remaining issues, why they matter, and whether they block the next task.
- **Next useful step:** one practical recommendation, without forcing a fixed milestone sequence.
- **Repository state (coding sessions):** branch, commit status if known, and whether changes are uncommitted, committed, pushed, merged, or deployed.

A future AI should be able to continue from the repository and this handoff without asking the user to repeat information already recorded.

## 9. Current known next step

Inspect the user's existing sample project/template for the React frontend and Django backend. The template's repository/files have not yet been supplied in the planning conversation, so its structure, dependencies, authentication, API, tests, security, and deployment configuration are **not yet verified**.

After inspection, identify only what genuinely needs to be decided before the web app can run and the first useful workflow can be built. Compare Vercel for the frontend, Render for the Django backend, and Supabase for managed PostgreSQL as candidates; do not treat any provider or topology as selected until verified against the template, costs, limits, security, and backup needs.

## 10. Project status and scope of this file

This is a living instruction file. Update it when the working process, confirmed architecture, security baseline, or major project direction changes. Keep feature-specific detail in the relevant requirement/decision documents rather than letting this file become the only source of truth.

The project is being planned incrementally. Treat the current default branch and its project records as the baseline, but check the actual GitHub branch and PR state before reporting repository status. No application implementation should be assumed to exist until the repository has been inspected.
