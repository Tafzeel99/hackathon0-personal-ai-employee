# Implementation Plan: Bronze Tier Foundation

**Branch**: `001-bronze-tier-foundation` | **Date**: 2026-02-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-bronze-tier-foundation/spec.md`

## Summary

Build the minimal working foundation of a local-first AI employee: an Obsidian vault folder structure with core Markdown files, a Python stdlib polling watcher that detects file drops in `watch_inbox/` and creates structured task files in `Needs_Action/`, and a Claude Code prompt template that processes tasks into plan files following `planning_skills.md`. No external dependencies, no network, no automation beyond the polling watcher.

## Technical Context

**Language/Version**: Python 3.8+ (stdlib + pathlib only)
**Primary Dependencies**: None — Python standard library only (pathlib, time, datetime, os)
**Storage**: Local filesystem — Markdown files in `AI_Employee_Vault/` directory hierarchy
**Testing**: Manual verification (drop file, inspect output); no test framework in Bronze
**Target Platform**: Local machine (Linux, macOS, or Windows with Python 3.8+)
**Project Type**: Single script + Markdown vault (no web/mobile components)
**Performance Goals**: Watcher detects new files within 15 seconds (one poll cycle)
**Constraints**: < 150 lines for watcher, zero pip installs, zero network, all intelligence in `agent_skills/*.md`
**Scale/Scope**: Single user, single machine, one vault folder, one watcher process

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Gate | Status |
| - | --------- | ---- | ------ |
| I | Local-First Architecture | All files in `AI_Employee_Vault/`; no cloud, no network, no remote DB | PASS |
| II | Minimal Viable Foundation | Only vault structure, watcher, task files, plan generation; nothing from Silver/Gold | PASS |
| III | Transparency and Auditability | All task files carry YAML frontmatter; watcher script has tier header comment; files traceable to triggers | PASS |
| IV | Human Remains in Control | Watcher only creates task files; human initiates Claude prompt; human moves files to Done/ | PASS |
| V | Spec-Driven Development | All intelligence in `agent_skills/planning_skills.md`; watcher handles only filesystem mechanics | PASS |

**Gate Result**: ALL PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-bronze-tier-foundation/
├── plan.md              # This file
├── research.md          # Phase 0 output — discrepancy resolutions
├── data-model.md        # Phase 1 output — entity schemas
├── quickstart.md        # Phase 1 output — setup and run guide
├── contracts/           # Phase 1 output — file format contracts
│   ├── task-file.md     # YAML frontmatter + body schema
│   └── plan-file.md     # Plan.md output format contract
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
AI_Employee_Vault/
├── Dashboard.md                    # FR-002: Status dashboard
├── Company_Handbook.md             # FR-003: Operational rules
├── Business_Goals.md               # FR-004: Quarter goals
├── agent_skills/
│   └── planning_skills.md          # FR-005: Plan format instructions
├── watch_inbox/                    # FR-006: Human drops files here
├── Needs_Action/                   # FR-008: Watcher creates task files here
├── In_Progress/                    # Placeholder for future use
├── Plans/                          # FR-015: Claude creates plans here
├── Done/                           # Completed tasks archived here
├── Inbox/                          # General incoming items (constitution)
└── Logs/                           # Optional log output

filesystem_watcher.py               # FR-006–FR-014: Polling watcher script
```

**Structure Decision**: Flat vault layout at project root. Single Python script alongside the vault. No `src/` or `tests/` directories — Bronze Tier uses manual verification only. The `In_Progress/` folder (from spec) and `Inbox/` folder (from constitution) are both created to satisfy both sources.

## Build Phases

### Phase A: Vault Structure (FR-001 through FR-005)

Create `AI_Employee_Vault/` with all subdirectories and four core Markdown files. Each file is independently verifiable by opening in Obsidian.

**Deliverables**:
1. `AI_Employee_Vault/` directory with 7 subdirectories + `Inbox/`
2. `Dashboard.md` with title, status section, recent plans section
3. `Company_Handbook.md` with three operational rules
4. `Business_Goals.md` with Q1 2026 goals
5. `agent_skills/planning_skills.md` with plan format specification

**Verification**: `ls -R AI_Employee_Vault/` shows exact structure; each `.md` opens correctly in Obsidian.

### Phase B: Filesystem Watcher (FR-006 through FR-014)

Single Python script using stdlib polling. Checks `watch_inbox/` every 15 seconds. Uses an in-memory set to track processed filenames and avoids duplicates.

**Deliverables**:
1. `filesystem_watcher.py` (< 150 lines, stdlib only)
2. Header comment per constitution code standards
3. Polling loop with 15-second interval
4. File detection for `.txt` and `.md` only
5. Task file creation in `Needs_Action/` with YAML frontmatter
6. Console logging of all activity

**Verification**: Run watcher, drop `test-task.txt`, confirm `TASK_test-task_<timestamp>.md` appears in `Needs_Action/` with valid frontmatter.

### Phase C: Claude Code Prompt Template (FR-015)

A prompt template (Markdown file) that a user can give to Claude Code to process pending tasks. Claude reads `Needs_Action/`, references `planning_skills.md`, and writes plan files to `Plans/`.

**Deliverables**:
1. Prompt template (stored in `agent_skills/` or project root)
2. Instructions for Claude to read tasks and generate plans per skill format

**Verification**: Run prompt with a task file present; confirm `Plans/Plan_<name>.md` appears with correct format.

### Phase D: End-to-End Validation

Integration test: file drop → watcher detect → task file → Claude prompt → plan file → move to Done/.

**Deliverables**:
1. Test script or manual steps documented
2. Confirmation that full flow works in < 2 minutes

**Verification**: Follow success verification steps from spec section 7.

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design artifacts were generated.*

| # | Principle | Post-Design Status | Notes |
| - | --------- | ------------------ | ----- |
| I | Local-First Architecture | PASS | All entities are local Markdown files. No network in any artifact. |
| II | Minimal Viable Foundation | PASS | Only 4 deliverable phases, all within Bronze scope. No Silver/Gold creep. |
| III | Transparency and Auditability | PASS | Task file contract includes 6 frontmatter fields. Plan file contract requires objective traceability. |
| IV | Human Remains in Control | PASS | Watcher only creates files. All processing and movement is human-initiated. |
| V | Spec-Driven Development | PASS | Intelligence in `planning_skills.md` and `process_tasks_prompt.md`. Watcher handles only filesystem mechanics. |

**Post-Design Gate Result**: ALL PASS — proceed to `/sp.tasks`.

## Complexity Tracking

No constitution violations detected. No complexity justifications needed.
