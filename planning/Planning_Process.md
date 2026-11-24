# {{PROJECT_NAME}} — Planning Process

**Status:** Adopted by {{OWNER}} on {{DATE}}  
**Purpose:** Define how {{PROJECT_NAME}} is planned before coding starts, following widely used software-engineering standards.  
**Progress tracking:** `Planning/Plan_Map.md` (overview) and `Planning/target_progress.md` (every item with its status)

## 1. Standards this process follows

| Area | Standard / practice | Used for |
|---|---|---|
| Requirements | ISO/IEC/IEEE 29148 | Stakeholders, use cases, verifiable functional requirements |
| Quality requirements | ISO/IEC 25010 | Security, performance, reliability, usability, maintainability, and other quality characteristics |
| Security | OWASP Application Security Verification Standard (ASVS) | Security requirements and release checklist |
| Architecture | C4 model + Architecture Decision Records (ADRs) | Context, container, and component views; recording each technical decision and its reason |
| API | OpenAPI specification | API contract shared by every client |
| Testing | ISO/IEC/IEEE 29119-3 structure | Test levels, techniques, environments, entry and exit criteria |
| Delivery | Incremental delivery with a user-story backlog | Small releasable increments, milestones, Definition of Done |

## 2. Planning steps

Each step depends on the steps before it. A later step may start early only when the dependency reason is recorded.

| # | Step | Artifact(s) | Location |
|---|---|---|---|
| 1 | Vision and scope | Project definition and amendments | `Planning/Foundation/project_definition.md` |
| 2 | Requirements | Actors, features, use cases, functional requirements | `Planning/Foundation/Requirements_Engineering/` |
| 3 | Quality requirements | Measurable non-functional requirements | `Planning/Foundation/Requirements_Engineering/quality_requirements.md` |
| 4 | Domain model | Concepts, identity, ownership, relationships, invariants, lifecycles | `Planning/Design/domain_model.md` |
| 5 | UX design | Screen inventory, user flows, low-fidelity wireframes | `Planning/Design/UX/ux_design.md` |
| 6 | Architecture | C4 diagrams, ADRs, hosting and deployment design | `Planning/Design/Architecture/` (ADRs in `ADR/`) |
| 7 | Data design | Schema, relationships, constraints, indexes, migrations, backup | `Planning/Design/data_design.md` |
| 8 | API design | OpenAPI contract, authentication, error format, versioning | `Planning/Design/API/` |
| 9 | Test strategy | Test levels, tools, coverage goals, critical suites | `Planning/Quality/test_strategy.md` |
| 10 | Delivery plan | Increments, user-story backlog, milestones, Definition of Done, CI/CD | `Planning/Delivery/delivery_plan.md` |
| 11 | Risk register | Risks, likelihood, impact, mitigation, triggers | `Planning/Delivery/risk_register.md` |
| 12 | Engineering standards | Coding conventions, simplicity rules, project structure, review checklist, AI assistant rules | `Planning/Engineering/engineering_handbook.md`, `AGENTS.md`, `CLAUDE.md` |

Coding starts only after steps 1–12 are complete, unless the owner explicitly decides otherwise.

### Supporting documents

| Document | Purpose |
|---|---|
| `Planning/Plan_Map.md` | Overview of every step; the entry point to the folder |
| `Planning/target_progress.md` | Status of every step, setup task, story, and milestone |
| `Planning/Decision_Log.md` | Every confirmed product decision (D-xx), proposed default (P-xx), and open question |
| `Planning/Delivery/setup_checklist.md` | Tasks only the owner can do: accounts, keys, repositories |
| `Planning/Design/Architecture/ADR/` | One Architecture Decision Record per technical decision |

## 3. Completion gate for every step

**Define → Draft → Review → Owner confirmation → Mark complete**

1. Define the scope of the step and what "done" means.
2. Draft the artifact.
3. Review it for consistency with earlier artifacts. Check that every ID it references exists.
4. Get the owner's explicit confirmation.
5. Mark the step complete in the Plan Map and in `target_progress.md`.

A draft is not complete because it exists. A step is complete only after owner confirmation.

## 4. Decision rules

- **Classify statements:** every important statement is a confirmed decision, a proposal, an open question, an assumption, or a constraint. Never turn a proposal or assumption into a decision without the owner's agreement.
- **Owner decides product matters:** anything that changes scope, user experience, security posture, cost, or architecture is decided by the owner.
- **Standard defaults for routine matters:** routine behavior follows established industry practice. It is drafted as a proposal (P-xx) and reviewed in groups, instead of blocking each step.
- **Record decisions:** a decision counts only when it is written into the document that owns it. Chat discussion alone does not count.
- **Change control:** to change a confirmed decision, identify the original, explain the impact, get confirmation, update every affected document, and mark the old decision superseded instead of erasing it. A change to scope is recorded as a numbered amendment in the project definition.
- **Keep the trackers current:** update the Plan Map and `target_progress.md` whenever a status changes.

## 5. Working method

- Work one step at a time, and within a step one area at a time.
- For each area, draft a proposal and list the open questions. The owner answers or corrects, then the document is updated.
- Ask product questions as short multiple-choice questions with a recommended option.
- After each step, run a consistency check: every referenced ID exists, no document still says "draft" for confirmed content, and no two documents contradict each other.
