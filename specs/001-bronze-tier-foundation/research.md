# Research: Bronze Tier Foundation

**Phase**: 0 — Outline & Research
**Date**: 2026-02-11
**Feature**: 001-bronze-tier-foundation

## Discrepancy Resolutions

Three discrepancies were found between the constitution and the spec. Each is resolved below.

### R-001: Task File Naming Convention

**Discrepancy**: Constitution says `TASK_<timestamp>_<filename>.md`, spec says `TASK_<original-name>_<timestamp>.md`.

- **Decision**: Use `TASK_<original-name>_<timestamp>.md` (spec convention)
- **Rationale**: Putting the human-readable name first makes it easier to find files visually in Obsidian. The timestamp suffix ensures uniqueness when the same file is dropped multiple times.
- **Alternatives considered**: Constitution's `TASK_<timestamp>_<filename>.md` would sort chronologically but is harder to scan by task name.

### R-002: Frontmatter Field Name — `source` vs `original_file`

**Discrepancy**: Constitution defines a `source` field (e.g., `watch_inbox/test-task.txt`). Spec defines `original_file` (e.g., `test-task.txt`).

- **Decision**: Include both fields — `source` (full relative path) and `original_file` (filename only)
- **Rationale**: `source` satisfies the constitution's traceability requirement. `original_file` satisfies the spec's explicit acceptance criteria. Both are useful: `source` for tracing origin, `original_file` for human readability.
- **Alternatives considered**: Using only one field would violate either the constitution or the spec.

### R-003: `In_Progress/` vs `Inbox/` Folder

**Discrepancy**: Spec lists `In_Progress/` but not `Inbox/`. Constitution lists `Inbox/` but not `In_Progress/`.

- **Decision**: Create both folders
- **Rationale**: Both are cheap (empty directories). `In_Progress/` is explicitly requested in the spec. `Inbox/` is in the constitution's vault structure. Neither violates any constraint. Creating both avoids breaking either source.
- **Alternatives considered**: Omitting one would violate its source document.

### R-004: Frontmatter `priority` Value — `medium` vs `normal`

**Discrepancy**: Spec acceptance criteria shows `priority: medium`. Constitution schema shows `priority: normal`.

- **Decision**: Use `medium` as the default value
- **Rationale**: The spec's acceptance criteria (section 6, item 5) explicitly shows `priority: medium` as the expected output. The constitution uses `normal` as one of the enum values. We adopt `medium` for the watcher default while acknowledging the constitution's valid values are `low | normal | high | urgent`. This is a minor naming difference; the watcher will use `medium` to match spec acceptance criteria exactly.
- **Alternatives considered**: Using `normal` would cause the spec acceptance test to fail.

## Technology Decisions

### T-001: Polling Implementation

- **Decision**: Use `time.sleep(15)` in a `while True` loop with `pathlib.Path.iterdir()`
- **Rationale**: Simplest possible approach using stdlib only. No threading, no async, no event system. Matches constitution constraint of polling over watchdog.
- **Alternatives considered**: `os.listdir()` (less ergonomic than pathlib), `select/poll` (unnecessary complexity for filesystem), `watchdog` (forbidden — external dependency).

### T-002: Duplicate Detection

- **Decision**: In-memory `set()` tracking processed filenames
- **Rationale**: Simple, zero-dependency, works for the single-session lifetime of the watcher. When watcher restarts, it re-processes existing files — this is acceptable in Bronze since manual oversight is expected.
- **Alternatives considered**: File-based tracking (`.processed` marker file) — adds complexity without clear benefit in Bronze. Checking if `TASK_*` already exists in `Needs_Action/` — fragile if files are moved.

### T-003: Timestamp Format

- **Decision**: `datetime.datetime.now().strftime("%Y%m%d_%H%M%S")` for filenames, ISO-8601 with timezone for frontmatter
- **Rationale**: Filename timestamps must be filesystem-safe (no colons). Frontmatter timestamps follow constitution's ISO-8601 requirement.
- **Alternatives considered**: Unix epoch (not human-readable), UUID (overkill).

### T-004: Claude Code Prompt Approach

- **Decision**: Store the processing prompt as `agent_skills/process_tasks_prompt.md` — a Markdown file the user can copy-paste or reference when running Claude Code
- **Rationale**: Follows the Agent Skills pattern. Intelligence stays in Markdown. The user runs Claude Code manually and points it at this prompt.
- **Alternatives considered**: Shell script wrapper (adds complexity), embedding in README (not discoverable), Python script calling Claude API (forbidden in Bronze).

## No Remaining Unknowns

All NEEDS CLARIFICATION items have been resolved. No further research needed.
