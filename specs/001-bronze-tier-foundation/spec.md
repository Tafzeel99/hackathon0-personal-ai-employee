# Feature Specification: Bronze Tier Foundation

**Feature Branch**: `001-bronze-tier-foundation`
**Created**: 2026-02-11
**Status**: Draft
**Input**: User description: "Bronze Tier foundation for Personal AI Employee — local-first Obsidian vault with file watcher, task creation, and Claude-driven plan generation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Vault Structure Setup (Priority: P1)

As a user, I want a ready-to-use Obsidian vault folder structure with core Markdown files so that my AI employee has a working memory and dashboard from day one.

**Why this priority**: Without the vault structure, nothing else can function. This is the foundation all other stories depend on.

**Independent Test**: Can be fully tested by opening the `AI_Employee_Vault/` folder in Obsidian and verifying all folders and core files render correctly with expected content.

**Acceptance Scenarios**:

1. **Given** the project directory exists, **When** the vault setup runs, **Then** `AI_Employee_Vault/` contains exactly these folders: `agent_skills/`, `watch_inbox/`, `Needs_Action/`, `In_Progress/`, `Plans/`, `Done/`, `Logs/`
2. **Given** the vault is created, **When** a user opens it in Obsidian, **Then** `Dashboard.md`, `Company_Handbook.md`, and `Business_Goals.md` exist at the vault root with their required content
3. **Given** the vault is created, **When** a user opens `agent_skills/planning_skills.md`, **Then** the file contains the plan format specification (objective, steps checklist, status fields)

---

### User Story 2 - File Drop Detection (Priority: P2)

As a user, I want to drop a `.txt` or `.md` file into `watch_inbox/` and have the filesystem watcher automatically detect it and create a structured task file in `Needs_Action/`.

**Why this priority**: This is the core trigger mechanism — the bridge between human intent and AI processing. Without it, no automated task pipeline exists.

**Independent Test**: Can be fully tested by running `filesystem_watcher.py`, dropping a text file into `watch_inbox/`, and confirming a corresponding `TASK_*.md` file appears in `Needs_Action/` within 15 seconds.

**Acceptance Scenarios**:

1. **Given** the watcher is running, **When** a user drops `test-task.txt` into `watch_inbox/`, **Then** within 15 seconds a file named `TASK_test-task_<timestamp>.md` appears in `Needs_Action/` with correct YAML frontmatter (type, created, status, priority, original_file)
2. **Given** the watcher is running, **When** a user drops a `.md` file into `watch_inbox/`, **Then** the watcher detects it and creates a corresponding task file just as it does for `.txt` files
3. **Given** the watcher has already processed a file, **When** the same file remains in `watch_inbox/` on the next poll, **Then** the watcher does NOT create a duplicate task file
4. **Given** the watcher is running, **When** a non-`.txt`/non-`.md` file is dropped into `watch_inbox/`, **Then** the watcher ignores it

---

### User Story 3 - Task Processing and Plan Generation (Priority: P3)

As a user, I want to run a Claude Code prompt that reads pending tasks from `Needs_Action/`, references the planning skill, and creates a structured plan file in `Plans/`.

**Why this priority**: This demonstrates the AI employee's core value — turning raw tasks into actionable plans. It requires Stories 1 and 2 to be complete first.

**Independent Test**: Can be fully tested by placing a task file in `Needs_Action/`, running the Claude Code processing prompt, and verifying a correctly formatted `Plan_*.md` appears in `Plans/`.

**Acceptance Scenarios**:

1. **Given** a task file exists in `Needs_Action/` with status "pending", **When** the user runs the Claude Code processing prompt, **Then** a `Plan_<original-name>.md` file is created in `Plans/` with objective, numbered steps, and status fields per `planning_skills.md`
2. **Given** the plan has been generated, **When** the user reviews it, **Then** the plan contains a one-sentence objective restating the task and a checkbox list of logical next actions
3. **Given** the plan has been generated, **When** the user moves the original task file to `Done/`, **Then** the end-to-end flow is complete and the task is archived

---

### User Story 4 - End-to-End Demo (Priority: P4)

As a user, I want to run the complete flow — drop a file, watch it get detected, process it with Claude, and see the finished plan — in under 2 minutes to prove the Bronze Tier works.

**Why this priority**: This is the integration test that validates all pieces work together. It depends on all previous stories.

**Independent Test**: Can be fully tested by running the watcher, dropping `test-task.txt` with content "Summarize my weekly tasks", processing the resulting task, and confirming the plan file in `Plans/`.

**Acceptance Scenarios**:

1. **Given** the vault structure is set up and the watcher is running, **When** the user drops `test-task.txt` with content "Summarize my weekly tasks" into `watch_inbox/`, **Then** within 15 seconds `Needs_Action/TASK_test-task_*.md` appears with correct frontmatter
2. **Given** the task file exists in `Needs_Action/`, **When** the user runs the Claude Code processing prompt, **Then** `Plans/Plan_test-task.md` is created with proper format
3. **Given** all steps complete successfully, **When** the user moves the task to `Done/`, **Then** the system outputs `BRONZE TIER FOUNDATION COMPLETE – READY FOR SILVER UPGRADE`

---

### Edge Cases

- What happens when `watch_inbox/` is empty? The watcher continues polling silently with no errors.
- What happens when a file with the same name is dropped again after being processed? The watcher creates a new task file with a different timestamp, avoiding collisions.
- What happens when `Needs_Action/` already contains a task file from a previous run? It is preserved; new files are added alongside existing ones.
- What happens when the watcher is started but the vault folders don't exist? The watcher should fail gracefully with a clear error message indicating missing directories.
- What happens when a file dropped into `watch_inbox/` is empty (0 bytes)? The watcher still creates a task file; the body content is simply empty.
- What happens when `Plans/` already contains a plan with the same name? The new plan uses a timestamped or incremented name to avoid overwriting.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create the `AI_Employee_Vault/` directory with exactly these subdirectories: `agent_skills/`, `watch_inbox/`, `Needs_Action/`, `In_Progress/`, `Plans/`, `Done/`, `Logs/`
- **FR-002**: System MUST create `Dashboard.md` at the vault root containing a title, status section with last activity date, and a recent plans section
- **FR-003**: System MUST create `Company_Handbook.md` at the vault root containing at least three operational rules for the AI employee
- **FR-004**: System MUST create `Business_Goals.md` at the vault root containing current quarter goals relevant to Bronze Tier
- **FR-005**: System MUST create `agent_skills/planning_skills.md` containing the plan format specification: objective (one sentence), steps (checkbox list), and status field
- **FR-006**: System MUST include a filesystem watcher script (`filesystem_watcher.py`) that polls `watch_inbox/` every 15 seconds for new `.txt` or `.md` files
- **FR-007**: Watcher MUST use only Python standard library and `pathlib` — no external dependencies
- **FR-008**: Watcher MUST create a task file in `Needs_Action/` for each newly detected file, named `TASK_<original-name>_<timestamp>.md`
- **FR-009**: Each task file MUST include YAML frontmatter with fields: type, created (ISO-8601), status (pending), priority (medium), and original_file
- **FR-010**: Task file body MUST contain the original file's content
- **FR-011**: Watcher MUST track which files have already been processed to prevent duplicate task creation
- **FR-012**: Watcher MUST ignore files that are not `.txt` or `.md`
- **FR-013**: Watcher MUST log its activity (files detected, tasks created, errors) to the console
- **FR-014**: Watcher script MUST be under 150 lines of code
- **FR-015**: A Claude Code prompt template MUST exist that reads `Needs_Action/` files, references `planning_skills.md`, and generates `Plan_<name>.md` files in `Plans/`

### Key Entities

- **Vault**: The root `AI_Employee_Vault/` folder — the single source of truth containing all state as Markdown files
- **Task File**: A Markdown file in `Needs_Action/` with YAML frontmatter metadata and body content from the original dropped file
- **Plan File**: A Markdown file in `Plans/` with objective, steps checklist, and status — generated by Claude following `planning_skills.md`
- **Agent Skill**: A Markdown file in `agent_skills/` that describes behavior for Claude to follow as instructions
- **Inbox File**: A raw `.txt` or `.md` file dropped by the user into `watch_inbox/` as a trigger

## Scope Boundary

### In Scope

- Obsidian vault folder structure creation
- Three core Markdown files (Dashboard, Handbook, Goals)
- One Agent Skill file (planning_skills.md)
- Python filesystem watcher using stdlib polling
- Task file creation with YAML frontmatter
- Claude Code prompt for plan generation
- Manual file movement to Done/

### Out of Scope

- Any API watchers (Gmail, WhatsApp, social media)
- MCP servers or external action execution
- Human-in-the-loop approval folders
- Ralph Wiggum persistence loop
- Scheduling, PM2, cron, daemons
- Odoo, accounting, social posting, CEO briefing
- JSON structured logs
- Error recovery beyond basic print/logging
- Automatic file movement by the watcher

## Assumptions

- User has Python 3.8+ installed on their local machine
- User has Obsidian installed (or any Markdown viewer) for viewing vault files
- User has Claude Code CLI available for running processing prompts
- The vault directory will be created within the project root directory
- The user will manually start/stop the watcher script
- File names dropped into `watch_inbox/` will use standard filesystem-safe characters
- The system operates on a single machine (no multi-user or networked access)

## Constraints

| Aspect           | Allowed in Bronze                   | Forbidden in Bronze                      |
| ---------------- | ----------------------------------- | ---------------------------------------- |
| Dependencies     | stdlib + pathlib                    | watchdog, requests, google-api, etc.     |
| Execution        | Manual prompt + watcher script      | Automatic orchestration, scheduling      |
| Claude interaction | Manual claude command              | API calls, persistent loop               |
| File movement    | Human or simple script              | Watcher moves files automatically        |
| Logs             | Optional simple .md or console      | JSON, append-only audit trail            |
| Intelligence     | agent_skills/*.md files             | Hardcoded logic in Python scripts        |
| Network          | None                                | Any network calls whatsoever             |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 7 vault subdirectories and 4 core Markdown files exist with correct content after setup — verified by directory listing and file inspection
- **SC-002**: Filesystem watcher detects a newly dropped file and creates a task file in `Needs_Action/` within 15 seconds of the file appearing
- **SC-003**: Task files contain valid YAML frontmatter with all required fields (type, created, status, priority, original_file) — verified by parsing
- **SC-004**: The watcher runs continuously without errors for at least 5 minutes of idle polling (no files dropped)
- **SC-005**: The watcher correctly ignores non-`.txt`/non-`.md` files — verified by dropping a `.jpg` file and confirming no task is created
- **SC-006**: Claude Code prompt produces a plan file with objective, checkbox steps, and status — verified by inspecting `Plans/` output
- **SC-007**: The complete end-to-end demo (file drop to plan file appearing) completes in under 2 minutes
- **SC-008**: The watcher script is under 150 lines and uses zero external dependencies — verified by line count and import inspection
- **SC-009**: No duplicate task files are created when the watcher polls the same unchanged `watch_inbox/` — verified by running watcher for 3+ poll cycles with the same file present
