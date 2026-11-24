# {{PROJECT_NAME}} — Domain Model

**Version:** 1.0  
**Status:** ⬜ Draft  
**Planning step:** 4 — Domain model  
**Method:** Domain-driven design vocabulary: bounded contexts, aggregates, entities, value objects, invariants. Diagrams use Mermaid, which GitHub renders.

## 1. Ubiquitous language

> **Guide:** the words that mean the same thing in requirements, design, code, and the user interface. Code must use these names and no synonyms.

| Term | Meaning |
|---|---|
| {{TERM}} | {{MEANING}} |

## 2. Bounded contexts

> **Guide:** group the domain into parts with clear responsibilities, for example Identity, Settings, the core domain, and reporting.

```mermaid
flowchart LR
  A[{{CONTEXT A}}] --> B[{{CONTEXT B}}]
```

| Context | Responsibility |
|---|---|
| {{CONTEXT}} | {{RESPONSIBILITY}} |

## 3. Domain class diagram

```mermaid
classDiagram
  class {{Entity}} {
    id
    {{attribute}}
  }
```

## 4. Aggregates

| Aggregate | Root | Contains | Consistency boundary |
|---|---|---|---|
| {{AGGREGATE}} | {{ROOT}} | {{PARTS}} | {{WHAT IS CHANGED TOGETHER}} |

## 5. Value objects

| Value object | Rules |
|---|---|
| {{e.g. Money}} | {{e.g. decimal amount plus currency; never floating point}} |

## 6. Invariants

> **Guide:** rules that must always be true. Each cites the requirement that defines it.

| ID | Invariant | Source |
|---|---|---|
| INV-01 | {{RULE}} | {{FR-ID}} |

## 7. Lifecycles

```mermaid
stateDiagram-v2
  [*] --> {{State}} : {{event}}
```

## 8. Domain services

| Service | Responsibility |
|---|---|
| {{SERVICE}} | {{RESPONSIBILITY}} |

## 9. Future extension points

- {{HOW THE MODEL ALLOWS A FUTURE FEATURE}}

## Change history

- **v1.0 ({{DATE}}):** First version.
