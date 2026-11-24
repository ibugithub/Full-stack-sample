# Planning Template

A reusable, standards-based planning kit for software projects. Copy it, rename it to `Planning/`, and fill it in step by step before writing code.

## What is inside

```
planning-template/
├── README.md                        this guide (delete after copying)
├── Plan_Map.md                      overview and entry point
├── Planning_Process.md              the 12-step process and decision rules (reusable as is)
├── Decision_Log.md                  product decisions, proposed defaults, open questions
├── target_progress.md               progress tracker for every step, task, and story
├── Foundation/
│   ├── project_definition.md        step 1: vision and scope
│   └── Requirements_Engineering/
│       ├── users.md                 step 2: actors
│       ├── features.md              step 2: capabilities
│       ├── use_cases_and_workflows.md   step 2: use cases
│       ├── functional_requirements.md   step 2: functional requirements
│       └── quality_requirements.md      step 3: quality requirements
├── Design/
│   ├── domain_model.md              step 4
│   ├── UX/ux_design.md              step 5
│   ├── Architecture/
│   │   ├── architecture.md          step 6
│   │   └── ADR/ADR-000-template.md  copy for every technical decision
│   ├── data_design.md               step 7
│   └── API/
│       ├── api_design.md            step 8
│       └── openapi.yaml             step 8: contract skeleton
├── Quality/test_strategy.md         step 9
├── Delivery/
│   ├── delivery_plan.md             step 10
│   ├── risk_register.md             step 11
│   └── setup_checklist.md           owner tasks: accounts, keys, repositories
├── Engineering/engineering_handbook.md  step 12: coding standards and structure
└── root-files/
    ├── AGENTS.md                    rules for AI coding assistants → copy to repo root
    └── CLAUDE.md                    loads AGENTS.md for Claude → copy to repo root
```

## How to use it

1. Copy the folder into the new project and rename it to `Planning/`.
2. Move `root-files/AGENTS.md` and `root-files/CLAUDE.md` to the repository root, then delete `root-files/`.
3. Replace every `{{PLACEHOLDER}}`. Search for `{{` to find them all.
4. Work through the steps **in order**, following `Planning_Process.md`. One step at a time; each step ends with your explicit confirmation.
5. Delete each `> **Guide:**` note once its section is filled in.
6. Record every product decision in `Decision_Log.md` and every technical decision as an ADR.
7. Keep `target_progress.md` up to date from the first day.
8. Start coding only after all 12 steps are confirmed.

## Conventions used in the templates

| Marker | Meaning |
|---|---|
| `{{PROJECT_NAME}}` | A placeholder to replace |
| `> **Guide:** …` | Instructions for filling the section; delete when done |
| A row containing `{{…}}` | An example row; replace it with real content, and add rows as needed |
| ✅ 🟡 ⬜ — | Done · in progress or awaiting confirmation · not started · not applicable |

## ID formats

| Prefix | Item | Document |
|---|---|---|
| ACT-xx | Actor | users.md |
| UC-xx | Use case | use_cases_and_workflows.md |
| FR-AREA-xxx | Functional requirement | functional_requirements.md |
| QR-AREA-xxx | Quality requirement | quality_requirements.md |
| INV-xx | Domain invariant | domain_model.md |
| S-xx, D-xx | Screen, dialog | ux_design.md |
| ADR-xxx | Architecture decision | Design/Architecture/ADR/ |
| D-xx | Confirmed product decision | Decision_Log.md |
| P-xx | Proposed default | Decision_Log.md |
| US-xxx | User story | delivery_plan.md |
| R-xx | Risk | risk_register.md |
| S-xx (setup) | Owner setup task | setup_checklist.md |

## Working with an AI assistant

A good opening instruction for each planning session:

> We are planning `{{PROJECT_NAME}}` using the `Planning/` folder. Read `Planning/Plan_Map.md` and `Planning/Planning_Process.md` first. We are on step `{{N}}`. Draft that step's document from the confirmed earlier steps. Ask me only about real product decisions, using short multiple-choice questions with a recommended option. Use standard defaults for routine matters and record them as proposals (P-xx) in the decision log. Do not start coding.
