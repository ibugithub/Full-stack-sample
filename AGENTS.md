# Instructions for AI coding assistants

These rules apply to every AI assistant that writes or changes code in this repository: Claude, ChatGPT, Codex, Cursor, Copilot, and others. Follow them exactly. When a rule here conflicts with your own habits, this file wins.

## 1. The project in short

{{ONE PARAGRAPH: what the product is, and its parts with their folders, for example "Backend: Django in the root; web app: Next.js in ui/".}}

All plans and decisions are in `Planning/`. Start with `Planning/Plan_Map.md`. Progress is tracked in `Planning/target_progress.md`.

## 2. The most important rule: keep the code simple

**Write code that a junior developer can understand in one reading.** Readable code is more important than short, clever, or "elegant" code. If you must choose between simple and smart, choose simple.

### Do

1. **Write the simplest code that meets the requirement.** Nothing extra "for later".
2. **Use clear, full names.** `total_amount`, not `ta`. Use the project's domain words from `Planning/Design/domain_model.md`.
3. **Keep functions focused.** One function does one job. If you need the word "and" to describe it, split it. There is no target size, but there are hard maximums, checked by the linters: **60 lines per function** (not counting blank lines and comments), **complexity 10** and **6 parameters** per function, and **400 lines per file**.
4. **Keep nesting shallow.** At most 3 levels inside a function. Use early returns instead of deep `if`/`else`.
5. **Be explicit.** Pass values as arguments; return results. Avoid hidden side effects and global state.
6. **Use the framework's normal way first.** Use standard features before writing your own.
7. **Follow the existing pattern.** Before writing a new file, look at a similar existing file and copy its structure.
8. **Write a short docstring** on every public function, class, and component: what it does in plain words and which requirement it implements, for example `(FR-AREA-001)`.
9. **Comment the "why", not the "what".**
10. **Handle errors clearly.** Raise or return a named error with a readable message. Never swallow an error silently.

### Do not

1. **No clever tricks.** No one-line puzzles, nested comprehensions, chained ternary expressions, or bit tricks.
2. **No early abstraction.** No base classes, generic helpers, factories, or design patterns until the same code is needed in three places.
3. **No "magic".** No metaprogramming, monkey-patching, dynamic attribute access, or reflection, unless an ADR requires it.
4. **No new dependencies** unless truly needed. Explain why in your summary.
5. **No unrelated changes.** Do not reformat, rename, or refactor code the task does not touch.
6. **No dead code.** No commented-out code or unexplained "TODO later" notes.

### Example

Hard to read:

```python
def t(r): return sum((x.e - x.s).seconds for x in r if not x.d) if r else 0
```

Easy to read:

```python
def total_tracked_seconds(records: list[TimeRecord]) -> int:
    """Total duration of the records that are not deleted, in seconds."""
    total = 0
    for record in records:
        if record.deleted_at is not None:
            continue
        duration = record.ended_at - record.started_at
        total += int(duration.total_seconds())
    return total
```

The easy version is longer, but anyone can read it from top to bottom and know exactly what it does.

## 3. Where code goes

Follow `Planning/Engineering/engineering_handbook.md`. In short:

- {{WHERE EACH KIND OF CODE LIVES, one bullet per codebase}}
- Business rules live only in {{THE BUSINESS-RULE LAYER}}.
- User data is always accessed through code that enforces ownership. Never trust a user or account ID sent by a client.

## 4. How to work on a task

1. **Find the story and requirements** in `Planning/Delivery/delivery_plan.md`. Read them before coding. If the task has no story, ask.
2. **Read the relevant ADR** in `Planning/Design/Architecture/ADR/`.
3. **Change the API contract first** if the task changes the API, then the backend, then every client.
4. **Write tests** with the requirement ID in the test name.
5. **Run the checks** for every part you changed: formatters, linters, type checks, tests. Fix every failure.
6. **Do one story at a time.** Keep each change small enough to review in one sitting.

## 5. Never do these

- Never start coding a new increment or story without the owner's explicit go-ahead.
- {{VERSION-CONTROL RULE, e.g. "Never run Git commands that change history or the remote; the owner does all Git work."}}
- Never put secrets, tokens, passwords, or `.env` contents in code, tests, logs, or messages.
- Never put real user data in the repository.
- Never change a planning decision on your own. If the code needs a different decision, stop and explain the problem.
- Never edit a database migration that is already released. Add a new one.
- Never weaken a test to make it pass.

## 6. When you finish

Report in plain language:

1. What you changed and why, with story and requirement IDs.
2. Which files you changed.
3. Which checks and tests you ran, and their results. Say clearly if something failed or was skipped.
4. Anything you were unsure about, or a decision the owner must make.

Then update `Planning/target_progress.md`: set the status of every part and story you worked on, refresh the summary and current focus, and add a dated line to the log.
