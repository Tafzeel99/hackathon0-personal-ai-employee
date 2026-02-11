# Tasks: Bronze Tier Foundation

**Input**: Design documents from `/specs/001-bronze-tier-foundation/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the feature specification. Manual verification only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Vault**: `AI_Employee_Vault/` at repository root
- **Script**: `filesystem_watcher.py` at repository root
- **Agent Skills**: `AI_Employee_Vault/agent_skills/`

---

## Phase 1: Setup

**Purpose**: Verify prerequisites exist before any implementation

- [x] T001 Verify Python 3.8+ is installed and accessible from the command line (`python --version` or `python3 --version`) — **DONE: Python 3.12.3**

---

## Phase 2: User Story 1 — Vault Structure Setup (Priority: P1) MVP

**Goal**: Create a ready-to-use Obsidian vault folder structure with core Markdown files so the AI employee has working memory and a dashboard.

**Independent Test**: Open `AI_Employee_Vault/` in Obsidian and verify all 8 subdirectories exist and all 4 Markdown files render correctly with their required content.

### Implementation for User Story 1

- [x] T002 [US1] Create `AI_Employee_Vault/` root directory and all 8 subdirectories: `agent_skills/`, `watch_inbox/`, `Needs_Action/`, `In_Progress/`, `Plans/`, `Done/`, `Inbox/`, `Logs/` — per plan.md project structure and research.md R-003 (both `In_Progress/` and `Inbox/` included)
- [x] T003 [P] [US1] Create `AI_Employee_Vault/Dashboard.md` with title "Personal AI Employee Dashboard – Bronze Tier", a Status section showing last activity date, and an empty Recent Plans section — per spec FR-002
- [x] T004 [P] [US1] Create `AI_Employee_Vault/Company_Handbook.md` with title "Company Handbook – Bronze Tier Rules" and three operational rules: (1) be polite and professional, (2) never take external actions without approval, (3) keep all data inside vault — per spec FR-003
- [x] T005 [P] [US1] Create `AI_Employee_Vault/Business_Goals.md` with title "Business Goals – Q1 2026 (Bronze)" and two goals: build working Bronze Tier AI Employee, demonstrate file-to-plan flow — per spec FR-004
- [x] T006 [P] [US1] Create `AI_Employee_Vault/agent_skills/planning_skills.md` with plan format specification: objective (one sentence), steps (checkbox list), status field, and a YAML frontmatter example matching `contracts/plan-file.md` — per spec FR-005

**Checkpoint**: Vault structure complete. Verify with `ls -R AI_Employee_Vault/` and open in Obsidian. All 8 subdirectories and 4 Markdown files must exist with correct content.

---

## Phase 3: User Story 2 — File Drop Detection (Priority: P2)

**Goal**: A filesystem watcher that polls `watch_inbox/` every 15 seconds and creates structured task files in `Needs_Action/` for each new `.txt` or `.md` file.

**Independent Test**: Run `python filesystem_watcher.py`, drop `test-task.txt` into `watch_inbox/`, confirm `TASK_test-task_<timestamp>.md` appears in `Needs_Action/` with valid YAML frontmatter within 15 seconds.

**Dependencies**: Requires Phase 2 (US1) complete — vault directories must exist.

### Implementation for User Story 2

- [x] T007 [US2] Create `filesystem_watcher.py` with Bronze Tier header comment per constitution code standards (`# Bronze Tier – Hackathon 0 – Personal AI Employee` / `# Generated following spec.constitution.md`), stdlib imports only (`pathlib`, `time`, `datetime`), and vault path constants (`VAULT_ROOT`, `WATCH_DIR`, `NEEDS_ACTION_DIR`) — per spec FR-006, FR-007, and constitution Code Standards
- [x] T008 [US2] Implement `main()` function in `filesystem_watcher.py` with: (a) startup validation that exits with clear error if `watch_inbox/` or `Needs_Action/` directories are missing, (b) `processed_files = set()` for in-memory duplicate tracking per research.md T-002, (c) `while True` polling loop that calls `scan_inbox()` then `time.sleep(15)` per research.md T-001, (d) `KeyboardInterrupt` handler for clean Ctrl+C shutdown — per spec FR-006, FR-011
- [x] T009 [US2] Implement `create_task_file(source_path)` in `filesystem_watcher.py` that: (a) reads source file content verbatim, (b) generates ISO-8601 timestamp with timezone for `created` field and filesystem-safe timestamp for filename per research.md T-003, (c) builds YAML frontmatter with all 6 required fields (`type: file_drop`, `created`, `status: pending`, `priority: medium`, `source: watch_inbox/<filename>`, `original_file: <filename>`) per `contracts/task-file.md`, (d) writes `Needs_Action/TASK_<name-without-ext>_<YYYYMMDD_HHMMSS>.md` with frontmatter + body per research.md R-001 — per spec FR-008, FR-009, FR-010
- [x] T010 [US2] Implement `scan_inbox()` in `filesystem_watcher.py` that: (a) iterates `watch_inbox/` with `pathlib.Path.iterdir()`, (b) filters to `.txt` and `.md` extensions only per spec FR-012, (c) skips files already in `processed_files` set per spec FR-011, (d) calls `create_task_file()` for new files and adds to set, (e) prints console log for each action (startup, each poll cycle, file detected, task created, errors) per spec FR-013 — per spec FR-006, FR-011, FR-012, FR-013
- [x] T011 [US2] Add `if __name__ == "__main__": main()` entry point in `filesystem_watcher.py`, verify script is under 150 lines with `wc -l`, confirm only stdlib imports, and manually test: drop `test-task.txt` with content "Summarize my weekly tasks" into `watch_inbox/`, verify `TASK_test-task_*.md` appears in `Needs_Action/` with all 6 frontmatter fields correct — **DONE: 117 lines, stdlib only, test passed** — per spec FR-014, SC-002, SC-003, SC-008

**Checkpoint**: Watcher works independently. Drop file, see task. Watcher ignores `.jpg`, doesn't duplicate on re-poll.

---

## Phase 4: User Story 3 — Task Processing and Plan Generation (Priority: P3)

**Goal**: A Claude Code prompt template that reads pending tasks from `Needs_Action/`, references `planning_skills.md`, and creates structured plan files in `Plans/`.

**Independent Test**: Place a task file in `Needs_Action/`, run the Claude Code prompt, verify `Plan_<name>.md` appears in `Plans/` with correct frontmatter (objective + status) and a Steps checkbox list per `contracts/plan-file.md`.

**Dependencies**: Requires Phase 2 (US1) complete — vault directories and `planning_skills.md` must exist.

### Implementation for User Story 3

- [x] T012 [US3] Create `AI_Employee_Vault/agent_skills/process_tasks_prompt.md` — a Claude Code prompt template that instructs Claude to: (a) list all `.md` files in `AI_Employee_Vault/Needs_Action/` with `status: pending` in frontmatter, (b) for each task read the body content, (c) read `AI_Employee_Vault/agent_skills/planning_skills.md` for output format, (d) generate `Plans/Plan_<original-name-without-TASK-prefix-and-timestamp>.md` with YAML frontmatter (`objective` + `status: complete`) and `## Steps` checkbox list per `contracts/plan-file.md`, (e) if `Plan_<name>.md` already exists append timestamp to avoid overwrite — per spec FR-015 and research.md T-004
- [x] T013 [US3] Manually verify prompt: create a sample `TASK_test-task_20260211_120000.md` in `Needs_Action/` per `contracts/task-file.md` with body "Summarize my weekly tasks", run Claude Code with the process_tasks_prompt instructions, confirm `Plans/Plan_test-task.md` appears with valid objective, `status: complete`, and at least 2 checkbox steps — **DONE: 5 steps, valid format** — per spec SC-006

**Checkpoint**: Task processing works. Claude reads task, generates plan in correct format.

---

## Phase 5: User Story 4 — End-to-End Demo (Priority: P4)

**Goal**: Execute the complete flow — file drop, watcher detection, task creation, Claude processing, plan generation, archive to Done — in under 2 minutes.

**Independent Test**: Start watcher, drop `test-task.txt`, confirm task file, run Claude prompt, confirm plan file, move task to `Done/`, verify timing under 2 minutes.

**Dependencies**: Requires Phase 2 (US1), Phase 3 (US2), and Phase 4 (US3) all complete.

### Implementation for User Story 4

- [x] T014 [US4] Execute full end-to-end demo: (1) start `python filesystem_watcher.py`, (2) create `watch_inbox/test-task.txt` with content "Summarize my weekly tasks", (3) wait up to 15 seconds and confirm `Needs_Action/TASK_test-task_*.md` exists with correct frontmatter, (4) run Claude Code with `process_tasks_prompt.md` instructions, (5) confirm `Plans/Plan_test-task.md` exists with correct format, (6) move task file to `Done/`, (7) verify entire flow completed in under 2 minutes — per spec section 7 verification steps and SC-007
- [x] T015 [US4] Update `AI_Employee_Vault/Dashboard.md` last activity date to current date after successful demo, and output exactly: `BRONZE TIER FOUNDATION COMPLETE – READY FOR SILVER UPGRADE` — per constitution milestone protocol

**Checkpoint**: End-to-end flow works. Bronze Tier is demonstrably functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification that all artifacts meet spec and constitution requirements

- [x] T016 Verify all vault files match spec minimum content requirements: Dashboard.md has status + recent plans sections, Handbook has 3 rules, Goals has 2 goals, planning_skills.md has format spec with example — per spec section 5
- [x] T017 Run `specs/001-bronze-tier-foundation/quickstart.md` validation steps to confirm documentation matches actual system behavior and all commands produce expected output

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US1 (Phase 2)**: Depends on Setup — creates vault structure that ALL other stories need
- **US2 (Phase 3)**: Depends on US1 — needs `watch_inbox/` and `Needs_Action/` directories
- **US3 (Phase 4)**: Depends on US1 — needs `agent_skills/` and `Plans/` directories (independent of US2)
- **US4 (Phase 5)**: Depends on US1 + US2 + US3 — integration test of all stories
- **Polish (Phase 6)**: Depends on US4 — final verification after demo

### User Story Dependencies

```
Phase 1: Setup
    │
    ▼
Phase 2: US1 (Vault Structure) ─── MVP
    │
    ├──────────────┐
    ▼              ▼
Phase 3: US2   Phase 4: US3    ← Can run in parallel!
(Watcher)      (Prompt Template)
    │              │
    └──────┬───────┘
           ▼
    Phase 5: US4 (End-to-End Demo)
           │
           ▼
    Phase 6: Polish
```

### Within Each User Story

- T002 must complete before T003–T006 (directories before files)
- T007 must complete before T008–T010 (scaffold before logic)
- T008, T009 must complete before T010 (core before integration)
- T010 must complete before T011 (logic before verification)

### Parallel Opportunities

- **Within US1**: T003, T004, T005, T006 can all run in parallel (different files, no dependencies)
- **Between US2 and US3**: Phase 3 and Phase 4 can run in parallel after US1 completes (watcher and prompt template are independent)
- **Within US2**: T008 and T009 could theoretically be parallel (different functions) but T010 integrates them, so sequential is safer for a single file

---

## Parallel Example: User Story 1

```bash
# After T002 (directories created), launch all Markdown files in parallel:
Task: "Create Dashboard.md in AI_Employee_Vault/Dashboard.md"
Task: "Create Company_Handbook.md in AI_Employee_Vault/Company_Handbook.md"
Task: "Create Business_Goals.md in AI_Employee_Vault/Business_Goals.md"
Task: "Create planning_skills.md in AI_Employee_Vault/agent_skills/planning_skills.md"
```

## Parallel Example: US2 + US3 after US1

```bash
# After US1 checkpoint passes, launch both stories in parallel:
Task: "Implement filesystem_watcher.py (US2 - Phase 3)"
Task: "Create process_tasks_prompt.md (US3 - Phase 4)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: US1 — Vault Structure (T002–T006)
3. **STOP and VALIDATE**: Open vault in Obsidian, verify all files
4. This alone is a useful, demonstrable artifact

### Incremental Delivery

1. US1 complete → Vault exists, opens in Obsidian (MVP)
2. US2 complete → Watcher detects files, creates tasks (automation layer)
3. US3 complete → Claude processes tasks into plans (AI layer)
4. US4 complete → Full flow works end-to-end (integration proof)
5. Each story adds value without breaking previous stories

### Suggested Execution Order

1. T001 (Setup)
2. T002 → T003+T004+T005+T006 in parallel (US1)
3. T007 → T008 → T009 → T010 → T011 (US2) — can overlap with US3
4. T012 → T013 (US3) — can overlap with US2
5. T014 → T015 (US4)
6. T016 → T017 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies on each other
- [Story] label maps each task to its user story for traceability
- All tasks reference specific file paths and contract documents
- Manual verification only — no automated test framework in Bronze
- Commit after each completed checkpoint (end of each Phase)
- US2 and US3 are independent and can be developed in parallel after US1
