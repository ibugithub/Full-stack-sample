# {{PROJECT_NAME}} — Engineering Handbook

**Version:** 1.0  
**Status:** ⬜ Draft  
**Planning step:** 12 — Engineering standards  
**Applies to:** all code in the repository  
**Based on:** {{STYLE GUIDES OF THE CHOSEN LANGUAGES, e.g. PEP 8, the official Kotlin conventions, the framework's documentation}}; Semantic Versioning for releases.

This handbook says **how** code is written and organized. **What** is built is defined by the requirements, and technical decisions by the ADRs. When this handbook and an ADR disagree, the ADR wins and this handbook is corrected.

> **Guide:** sections 1, 1A, 1B, 9, 10, and 11 are general and usually kept as they are. Fill in sections 2 to 8 for the project's stack.

---

## 1. Universal rules

1. **Requirements first.** Every change traces to a user story (US-xxx) and its requirements.
2. **One rule, one place.** Business rules live in one layer, normally the backend service layer. Clients never re-implement them, except for instant form hints that the server re-checks.
3. **Data ownership always.** User data is reached only through code that enforces ownership.
4. **No secrets in code.** Configuration comes from environment variables or secret stores.
5. **No personal data in logs.**
6. **Focused units with hard maximums.** Functions do one thing, within the limits in section 1B.
7. **Names over comments.** Comments explain *why*, never *what*. Public functions and classes have a short docstring.
8. **Same names everywhere.** Domain terms come from the ubiquitous language in the domain model. No synonyms.
9. **Tests are part of the change.**
10. **Automated formatting.** Formatters decide formatting, not reviewers.
11. **Legacy code.** Existing code that does not follow these rules is changed only when a story touches it anyway.

## 1A. Simplicity and readability

The main quality goal for all code is that **anyone can understand it easily**, including a junior developer seeing it for the first time. Simple code is preferred over short or clever code, for code written by people and by AI assistants.

| Rule | Meaning |
|---|---|
| Simplest solution | Build only what the requirement needs, nothing "for later" |
| Clear names | Full words and domain terms; no abbreviations |
| Focused functions | One job each, within the maximums in section 1B |
| Shallow nesting | Use early returns instead of deep if/else |
| Explicit code | Values in as arguments and out as results; no hidden side effects or global state |
| Framework first | Use the framework's standard features before custom code |
| No early abstraction | No base classes, generic helpers, or patterns until code repeats in three places |
| No clever tricks | No one-line puzzles, nested comprehensions, chained ternaries, or metaprogramming |
| Follow existing patterns | New files copy the structure of a similar existing file |

AI assistants follow these rules through `AGENTS.md` at the repository root. `CLAUDE.md` loads `AGENTS.md` for Claude. Any change to these rules is made in both places.

In code review, "I had to read this twice" is a valid reason to ask for a simpler version.

## 1B. Size and complexity limits

These are **maximums**, not targets, enforced by the linters in CI. They follow widely used thresholds: 60 lines is the default of detekt's `LongMethod` rule, 50 statements the default of Ruff's `PLR0915`, and 10 the complexity limit recommended by McCabe. Most code should stay well below them.

| Limit | Maximum |
|---|---|
| Function length | 60 lines, not counting blank lines and comments |
| Cyclomatic complexity | 10 per function |
| Parameters | 6 per function |
| Nesting depth | 3 levels inside a function |
| File length | 400 lines |

> **Guide:** map each limit to the linter rule of every language used. For example, Python with Ruff: `PLR0915`, `C901`, `PLR0913`. TypeScript with ESLint: `max-lines-per-function`, `complexity`, `max-params`, `max-depth`, `max-lines`. Kotlin with detekt: `LongMethod`, `CyclomaticComplexMethod`, `LongParameterList`, `NestedBlockDepth`.

- Generated code, migrations, and test data files are excluded.
- Going over a limit needs a one-line comment explaining why, approved in review. A limit is never silently disabled.

## 2. Repository structure

> **Guide:** the full top-level tree with one line per folder. State that new top-level folders need an ADR, and that user data never lives in the repository.

```
{{PROJECT_NAME}}/
├── README.md
├── AGENTS.md                      rules for AI coding assistants
├── CLAUDE.md                      loads AGENTS.md for Claude
├── {{FOLDER}}/                    {{PURPOSE}}
└── Planning/                      planning documents
```

## 3. {{BACKEND LANGUAGE AND FRAMEWORK}}

> **Guide:** for each codebase, fill in four parts:
> 1. **Versions and tools:** language version, framework, formatter, linter, type checker, test tools, dependency pinning.
> 2. **Module layout:** the files every module contains, and what each file may and may not do.
> 3. **Layer rules:** a table of "may" and "must not" per layer, for example views, services, queries, models.
> 4. **Naming:** a table of naming styles with examples.

## 4. {{WEB CLIENT}}

> **Guide:** same four parts as section 3, plus rules for server data, client state, forms, styling, texts, dates and money, accessibility, and errors.

## 5. {{MOBILE OR OTHER CLIENT}}

> **Guide:** same four parts, plus the dependency rule between modules. Delete this section if there is no such client.

## 6. API contract workflow

1. Change the API contract first.
2. Implement the backend change and its tests; CI checks the implementation against the contract.
3. Update every client.
4. Breaking changes are not allowed within an API version.

## 7. Testing conventions

| Codebase | Location | Naming |
|---|---|---|
| {{CODEBASE}} | {{WHERE TESTS LIVE}} | {{e.g. test_fr_area_001_does_something}} |

- Each test checks one behavior, with an arrange, act, assert structure.
- Test data comes from factories, never from production data.
- A bug fix starts with a failing test that reproduces it.

## 8. Version control

> **Guide:** state who manages version control and any conventions the automation depends on, such as release tags that trigger builds. If the owner manages version control personally, say so and prescribe nothing else.

## 9. Code review checklist

- [ ] Easy to understand in one reading: clear names, focused functions, shallow nesting, no clever tricks (section 1A), within the limits of section 1B.
- [ ] Traces to a story and its requirements; tests are tagged with the requirement IDs.
- [ ] Business rules are in the right layer.
- [ ] User data is accessed only through ownership-enforcing code, with tests.
- [ ] Every client is consistent with the contract.
- [ ] Loading, empty, error, and offline states are handled.
- [ ] No secrets, tokens, or personal data in code, logs, or fixtures.
- [ ] Migrations are reversible and named.
- [ ] Accessibility: labels, focus order, contrast, touch targets.
- [ ] Documentation and `Planning/target_progress.md` updated.

## 10. Documentation conventions

| Document | When |
|---|---|
| Root `README.md` | Overview, quick start, links to each part |
| Part READMEs | Setup steps and what the part owns |
| ADR | Every new or changed technical decision; never deleted, only superseded |
| Decision Log | Every product decision |
| Docstrings | Public functions, classes, and components, naming the requirement they implement |
| `CHANGELOG.md` | One section per release |

## 11. Security coding rules

- Validate all input on the server, whatever the client checks.
- Use the ORM or parameterized queries; never build SQL from strings.
- Never render user input as raw HTML.
- Never trust a client-supplied user or account ID.
- Store no credential in readable browser storage or plain device storage.
- Add dependencies only when needed; check license and maintenance; keep versions pinned.

## 12. Developer tooling

| Tool | Purpose |
|---|---|
| `.editorconfig` | Encoding, line endings, indentation per language |
| pre-commit hooks | Formatters, linters, and a secret scan on staged files |
| {{TOOL}} | {{PURPOSE}} |

## Change history

- **v1.0 ({{DATE}}):** First version.
