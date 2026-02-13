# Tasks: Silver Tier Functional Assistant

**Input**: Design documents from `/specs/002-silver-tier-assistant/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: No test framework in Silver scope (manual end-to-end demo verification).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Project Configuration)

**Purpose**: Dependencies, environment config, vault folder extension

- [x] T001 Create requirements.txt at project root with: google-api-python-client, google-auth-oauthlib, google-auth-httplib2, python-dotenv
- [x] T002 [P] Create .env.example at project root with template variables: GMAIL_CREDENTIALS_FILE, GMAIL_TOKEN_FILE, GMAIL_POLL_INTERVAL, DRY_RUN
- [x] T003 [P] Verify .gitignore includes: .env, .env.*, credentials.json, token.json
- [x] T004 Create Silver vault folders: AI_Employee_Vault/Pending_Approval/, AI_Employee_Vault/Approved/, AI_Employee_Vault/Rejected/, AI_Employee_Vault/Briefings/
- [x] T005 [P] Add .gitkeep files to new empty vault folders so git tracks them

**Checkpoint**: Project config complete. pip install -r requirements.txt works. Vault has all Silver folders.

---

## Phase 2: Foundational (Shared Infrastructure)

**Purpose**: Logging utility and Agent Skills that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Create log_utils.py at project root — shared JSONL logging utility (< 50 lines). Must provide: `log_event(action, source, result, task_ref=None, details=None)` function that appends a JSON object to AI_Employee_Vault/Logs/YYYY-MM-DD.json per contracts/log-entry.md schema
- [x] T007 [P] Create AI_Employee_Vault/agent_skills/email_skills.md — email handling rules: when to suggest reply vs forward vs archive, tone guidelines, how to extract sender/subject/body for task files, email reply drafting format
- [x] T008 [P] Create AI_Employee_Vault/agent_skills/approval_skills.md — HITL threshold rules: which actions require approval (all email_send, all post_linkedin), approval file format per contracts/approval-request-file.md, when to set action_required=yes in Plan.md
- [x] T009 [P] Create AI_Employee_Vault/agent_skills/social_post_skills.md — LinkedIn drafting rules: professional tone, 100-300 words, must include call-to-action, Karachi/Pakistan business context when relevant, hashtag guidelines
- [x] T010 Update AI_Employee_Vault/Company_Handbook.md — add HITL rules section: all external actions require approval via Pending_Approval folder, human moves to Approved or Rejected, no auto-execution
- [x] T011 [P] Update AI_Employee_Vault/Business_Goals.md — add weekly review cadence: CEO Briefing generated Mondays, review Done/ tasks weekly

**Checkpoint**: log_utils.py importable. All 3 new Agent Skills readable. Vault content updated with HITL and scheduling references.

---

## Phase 3: User Story 1 - Gmail Watcher (Priority: P1)

**Goal**: Detect incoming Gmail messages and create task files in Needs_Action/

**Independent Test**: Start gmail_watcher.py with valid OAuth credentials. Send a test email. Within 120 seconds, EMAIL_*.md appears in Needs_Action/ with correct frontmatter and body content.

### Implementation for User Story 1

- [x] T012 [US1] Create gmail_watcher.py at project root (< 150 lines). Implement: OAuth authentication using google-auth-oauthlib (credentials.json → token.json), --auth-only flag for first-time setup, --dry-run flag. Load config from .env via python-dotenv with os.environ fallback. Reference contracts/email-task-file.md for output format
- [x] T013 [US1] Implement polling loop in gmail_watcher.py: poll Gmail inbox every GMAIL_POLL_INTERVAL seconds (default 120), list unread messages using Gmail API users.messages.list(q='is:unread'), track processed message IDs in memory to prevent duplicates
- [x] T014 [US1] Implement email-to-task-file creation in gmail_watcher.py: for each unread message, extract from/subject/body (prefer text/plain, strip HTML fallback), create AI_Employee_Vault/Needs_Action/EMAIL_<YYYYMMDD>_<HHMMSS>_<subject_slug>.md with frontmatter per contracts/email-task-file.md, mark email as read via Gmail API (skip in dry-run), log each detection via log_utils.log_event
- [x] T015 [US1] Add error handling to gmail_watcher.py: catch auth failures (log + retry next cycle), catch rate limits (log + double interval temporarily), catch network errors (log + continue), handle empty subject/body with fallbacks per data-model.md validation rules, graceful Ctrl+C shutdown

**Checkpoint**: Gmail watcher runs, detects unread emails, creates EMAIL_*.md files, marks as read, logs events. Filesystem watcher (Bronze) still works independently.

---

## Phase 4: User Story 2 - Orchestrator with HITL (Priority: P2)

**Goal**: Claim tasks, invoke Claude Code, route external actions through approval workflow

**Independent Test**: Place a task file in Needs_Action/. Run orchestrator.py. Confirm: file moves to In_Progress/, Plan.md appears in Plans/, approval file appears in Pending_Approval/ if action_required. Move to Approved/ and confirm detection.

### Implementation for User Story 2

- [x] T016 [US2] Create orchestrator.py at project root (< 150 lines). Implement main polling loop: scan AI_Employee_Vault/Needs_Action/ for task files, claim first found by shutil.move to AI_Employee_Vault/In_Progress/ (catch FileNotFoundError for race condition), process sequentially one at a time, --dry-run flag, load .env config
- [x] T017 [US2] Implement Claude Code invocation in orchestrator.py: read task file content + relevant agent_skills/*.md files, build prompt string with task context + skills, call Claude Code CLI via subprocess.run, capture stdout, write Plan.md to AI_Employee_Vault/Plans/ with frontmatter per data-model.md Plan File schema
- [x] T018 [US2] Implement Ralph Wiggum loop in orchestrator.py: wrap Claude invocation in for-loop (MAX_ITERATIONS=20 constant), after each iteration check stdout for TASK_COMPLETE marker, if found break and move task to Done/, if limit reached log loop_warning via log_utils and move task to Done/ with status incomplete
- [x] T019 [US2] Implement HITL detection in orchestrator.py: after Plan.md is generated, parse frontmatter for action_required=yes, if yes create approval file in AI_Employee_Vault/Pending_Approval/ per contracts/approval-request-file.md, extract action_type/target/content from Plan.md body, log approval_created event
- [x] T020 [US2] Implement approval polling in orchestrator.py: in main loop, scan AI_Employee_Vault/Approved/ for files — dispatch to appropriate MCP handler. Scan AI_Employee_Vault/Rejected/ — log rejection, update task frontmatter status to rejected, move task+plan+rejection to AI_Employee_Vault/Done/
- [x] T021 [US2] Implement non-HITL completion path in orchestrator.py: when plan has action_required=no, move task from In_Progress/ and plan from Plans/ to AI_Employee_Vault/Done/, log task completion via log_utils

**Checkpoint**: Orchestrator claims tasks, invokes Claude, generates plans, creates approval files for HITL tasks, handles approved/rejected paths, processes non-HITL tasks to Done/.

---

## Phase 5: User Story 3 - Email MCP (Priority: P3)

**Goal**: Send or draft Gmail messages after HITL approval

**Independent Test**: Place a pre-formatted approval file in Approved/ with hitl_type: email_send. Run orchestrator. Confirm email is sent (or logged in dry-run), result logged, approval moved to Done/.

### Implementation for User Story 3

- [x] T022 [US3] Create email_mcp.py at project root (< 150 lines). Implement Gmail API send/draft operations: accept CLI args (--to, --subject, --body, --draft-only, --dry-run), authenticate using same OAuth flow as gmail_watcher (shared credentials.json/token.json), send email via Gmail API users.messages.send or create draft via users.drafts.create
- [x] T023 [US3] Implement dry-run mode in email_mcp.py: when --dry-run flag is set, log full email details (to, subject, body preview) but do NOT call Gmail API, output JSON result to stdout: {"status": "dry_run", "to": "...", "subject": "..."}
- [x] T024 [US3] Implement error handling in email_mcp.py: catch API errors (auth, rate limit, invalid recipient), return JSON error result to stdout for orchestrator to parse, log failures via log_utils.log_event with action=email_failed
- [x] T025 [US3] Wire email MCP into orchestrator.py approval handler: when approved file has action_type=email_send or email_draft, extract target/subject/body from approval file, call email_mcp.py via subprocess with appropriate args, parse JSON result, log email_sent or email_failed, move approval file + related task to AI_Employee_Vault/Done/

**Checkpoint**: End-to-end email flow works: Gmail watcher detects email → orchestrator creates plan + approval → human approves → email MCP sends (or drafts) → logged → moved to Done/.

---

## Phase 6: User Story 4 - LinkedIn Post Drafting (Priority: P4)

**Goal**: Claude drafts LinkedIn posts in Plan.md, creates approval file for HITL

**Independent Test**: Drop file "Draft a LinkedIn post about AI automation" in watch_inbox/. After processing, Plan.md has LinkedIn Post Draft section, approval file in Pending_Approval/ with full post text.

### Implementation for User Story 4

- [x] T026 [US4] Verify social_post_skills.md created in T009 instructs Claude to: detect social/LinkedIn keywords in tasks, add "LinkedIn Post Draft" section to Plan.md (100-300 words, professional tone, CTA, hashtags), set action_required=yes and hitl_type=post_linkedin in plan frontmatter
- [x] T027 [US4] Wire LinkedIn approval into orchestrator.py: when approved file has action_type=post_linkedin, log the approved content as "ready for manual posting" via log_utils with action=post_linkedin_approved, move approval + task to AI_Employee_Vault/Done/ (no MCP call — draft-only in Silver per research.md T-007)
- [x] T028 [US4] Create a test scenario file AI_Employee_Vault/watch_inbox/test-linkedin-post.txt with content: "Draft a LinkedIn post about how our team is using AI automation to improve business operations in Karachi" — verify end-to-end flow produces plan with draft + approval file

**Checkpoint**: LinkedIn post drafting works via Claude + social_post_skills.md. Approval file shows full draft text. Approved posts logged as ready for manual posting.

---

## Phase 7: User Story 5 - Weekly CEO Briefing (Priority: P5)

**Goal**: Generate weekly briefing summarizing Done/ tasks, pending items, and proactive suggestion

**Independent Test**: Place several completed tasks in Done/ with various dates. Run briefing_generator.py or orchestrator.py --generate-briefing. Confirm Briefings/Monday_YYYY-MM-DD.md appears with all 3 sections.

### Implementation for User Story 5

- [x] T029 [US5] Create briefing_generator.py at project root (< 150 lines). Implement: scan AI_Employee_Vault/Done/ for files with created date in last 7 days, parse frontmatter to extract type/status/objective, group by type (email_inbound, file_drop, scheduled), count totals
- [x] T030 [US5] Implement briefing file generation in briefing_generator.py: create AI_Employee_Vault/Briefings/Monday_YYYY-MM-DD.md with frontmatter per contracts/briefing-file.md (type, period_start, period_end, generated, task_count), body sections: Completed Tasks Summary (grouped by type), Pending Items (scan Needs_Action/ + In_Progress/), Proactive Suggestion (one recommendation based on task patterns)
- [x] T031 [US5] Add --generate-briefing flag to orchestrator.py: when flag is passed, call briefing_generator.py logic (import or subprocess), generate briefing immediately and exit. Also add schedule check in main loop: if current day is Monday and no briefing exists for today, auto-generate
- [x] T032 [US5] Log briefing generation via log_utils.log_event with action=briefing_generated, include task_count and output path in details

**Checkpoint**: Briefing generation works manually and on Monday schedule. File has all 3 sections. Log entry confirms generation.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Dashboard update, end-to-end verification, cleanup

- [x] T033 Update AI_Employee_Vault/Dashboard.md — add Silver sections: Pending Approval Queue (count of files in Pending_Approval/), Latest Briefing (link to most recent Briefings/ file), Silver Tier Status (watchers running, orchestrator active)
- [x] T034 [P] Update AI_Employee_Vault/agent_skills/planning_skills.md — add Silver extensions: Approval Required section format (when action_required=yes), LinkedIn Post Draft section format, reference to approval_skills.md for HITL threshold rules
- [x] T035 Run end-to-end demo verification per quickstart.md: Test A (file drop → plan → Done), Test B (email → plan → approval → MCP send → Done), Test C (LinkedIn draft → approval → logged), Test D (briefing generation). Confirm all logs present in Logs/YYYY-MM-DD.json
- [x] T036 Verify all Python scripts have Silver header comment: "# Silver Tier – Hackathon 0 – Personal AI Employee / # Generated following spec.constitution.md" and --dry-run flag documented. Verify each script is < 150 lines
- [x] T037 Output: SILVER TIER FUNCTIONAL ASSISTANT COMPLETE – READY FOR GOLD UPGRADE

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 Gmail Watcher (Phase 3)**: Depends on Phase 2 (needs log_utils, email_skills)
- **US2 Orchestrator (Phase 4)**: Depends on Phase 2 (needs log_utils, approval_skills) + US1 is helpful but not blocking (orchestrator also handles file drop tasks)
- **US3 Email MCP (Phase 5)**: Depends on US2 (orchestrator must exist to dispatch)
- **US4 LinkedIn Draft (Phase 6)**: Depends on US2 (orchestrator must exist) + social_post_skills from Phase 2
- **US5 CEO Briefing (Phase 7)**: Depends on Phase 2 (needs log_utils) — can start after Phase 2 but best after some Done/ tasks exist
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — fully independent, no other story needed
- **US2 (P2)**: After Phase 2 — independent of US1 (can process file_drop tasks)
- **US3 (P3)**: After US2 — needs orchestrator approval dispatch
- **US4 (P4)**: After US2 — needs orchestrator HITL flow
- **US5 (P5)**: After Phase 2 — independent (reads Done/ directly)

### Within Each User Story

- Models/contracts define the file formats (already in contracts/)
- Infrastructure tasks (log_utils, skills) before scripts
- Core functionality before error handling
- Wire into orchestrator after standalone functionality works

### Parallel Opportunities

Phase 1:
```
T001 → T004 (sequential: install deps before vault folders)
T002, T003, T005 → all [P] can run in parallel
```

Phase 2:
```
T006 (log_utils) → must complete first (all stories import it)
T007, T008, T009, T010, T011 → all [P] can run in parallel after T006
```

User Stories (after Phase 2):
```
US1 (Phase 3) and US5 (Phase 7) can run in parallel
US2 (Phase 4) can start alongside US1
US3 and US4 must wait for US2
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US1 — Gmail Watcher
4. Complete Phase 4: US2 — Orchestrator + HITL
5. **STOP and VALIDATE**: Email → task → plan → approval flow works
6. Demo: File drop + email detection + plan generation + HITL routing

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. US1 → Gmail watcher detects emails → Demo!
3. US2 → Orchestrator processes tasks with HITL → Demo!
4. US3 → Email MCP sends after approval → Demo!
5. US4 → LinkedIn draft via Agent Skills → Demo!
6. US5 → Weekly CEO Briefing → Demo!
7. Polish → End-to-end verification → SILVER COMPLETE

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story is independently testable after completion
- No test framework tasks (manual demo verification per spec)
- All scripts must stay under 150 lines per constitution
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
