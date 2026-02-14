# Tasks: Gold Tier Autonomous Employee

**Input**: Design documents from `/specs/003-gold-tier-autonomous-employee/`
**Prerequisites**: spec.md (complete), constitution.md (Gold v3.0.0), existing Silver codebase

**Tests**: Not explicitly requested — test tasks omitted. Each user story includes an Independent Test description for manual validation.

**Organization**: Tasks grouped by user story (6 stories from spec.md) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Root-level scripts**: `*.py` at repository root (established Silver pattern)
- **Vault**: `AI_Employee_Vault/` with subfolders
- **Agent Skills**: `AI_Employee_Vault/agent_skills/*.md`
- **Specs**: `specs/003-gold-tier-autonomous-employee/`

---

## Phase 1: Setup (Shared Infrastructure for Gold)

**Purpose**: Extend the existing Silver vault and project structure with Gold-required folders, dependencies, and configuration.

- [x] T001 Create new vault folders: `AI_Employee_Vault/Quarantine/`, `AI_Employee_Vault/Alerts/`, `AI_Employee_Vault/Odoo_Drafts/` with `.gitkeep` files
- [x] T002 [P] Update `requirements.txt` to add Gold dependencies: `odoorpc`, `facebook-sdk`, `tweepy`, `requests-oauthlib`
- [x] T003 [P] Create `.env.example` with all Gold credential placeholders: `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD`, `FB_PAGE_ACCESS_TOKEN`, `FB_PAGE_ID`, `IG_ACCESS_TOKEN`, `IG_BUSINESS_ACCOUNT_ID`, `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` (plus existing Gmail vars)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and patterns that ALL user stories depend on. MUST complete before any user story work begins.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Create `retry_handler.py` — shared retry utility with exponential backoff (1s, 2s, 4s, max 60s, max 3 retries). Must accept a callable + args, return result or raise after exhaustion. Must log each retry via `log_utils.log_event`. Must support transient error detection (HTTP 429, 500, 503). < 80 lines.
- [x] T005 [P] Extend `log_utils.py` — add richer `details` support: accept a `dict` for details (not just string), include fields for `mcp_params`, `response_snippet`, `odoo_record_id`, `social_post_id`, `retry_count`. Maintain backward compatibility with existing string details.
- [x] T006 [P] Create `quarantine_utils.py` — shared utility for moving tasks to `Quarantine/` with error details added to frontmatter, and creating alert files in `Alerts/` with human-readable description and suggested remediation. < 60 lines.
- [x] T007 [P] Create `AI_Employee_Vault/agent_skills/recovery_skills.md` — Agent Skill describing retry policies, quarantine criteria, watchdog behavior, alert file format, and graceful degradation rules per FR-033.
- [x] T008 Update `AI_Employee_Vault/agent_skills/approval_skills.md` — expand HITL triggers for Gold: add `odoo_confirm`, `odoo_payment`, `post_facebook`, `post_instagram`, `post_x` action types. Add threshold-based escalation rules (payment amount, unusual patterns).
- [x] T009 Update `orchestrator.py` — add `ensure_dirs()` to include `Quarantine/`, `Alerts/`, `Odoo_Drafts/`. Update header to Gold Tier. Raise `MAX_ITER` from 20 to 50. Add domain-based dispatch routing skeleton (email, social, erp). Update argparser description to Gold Tier.

**Checkpoint**: Foundation ready — retry handler, extended logging, quarantine utilities, and expanded HITL skills in place. User story implementation can now begin.

---

## Phase 3: User Story 1 — Odoo ERP Invoice & Payment Flow (Priority: P1) MVP

**Goal**: Enable the AI employee to draft invoices/payments in a local Odoo instance via JSON-RPC, route through HITL approval, and confirm/post after approval.

**Independent Test**: Drop a file "Create invoice for Client X, PKR 50,000 for consulting services" into `watch_inbox/`. Verify: orchestrator invokes Claude, Claude drafts invoice via Odoo MCP, approval file appears in `Pending_Approval/` with invoice details. Move to `Approved/`. Verify Odoo invoice is confirmed, vault log records the full chain, and a local copy exists in `Odoo_Drafts/`.

### Implementation for User Story 1

- [x] T010 [US1] Create `odoo_mcp.py` — Odoo MCP server with JSON-RPC client. CLI interface: `--action {create_invoice, create_payment, confirm_invoice, confirm_payment, list_invoices, list_payments, get_partner}`, `--data <json>`, `--dry-run`. Use `odoorpc` library (fallback to `xmlrpc.client`). Load credentials from `.env` (`ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD`). Return JSON to stdout. Log all operations via `log_utils.log_event`. Include Gold header comment. < 200 lines.
- [x] T011 [US1] Create `AI_Employee_Vault/agent_skills/odoo_skills.md` — Agent Skill describing: when to create an invoice vs payment, required fields (partner, product lines, amounts, reference), validation rules, when to flag for HITL, Odoo field mappings, error patterns to watch for. Per FR-030.
- [x] T012 [US1] Extend `orchestrator.py` — add Odoo dispatch in `handle_approved()`: detect `action_type: odoo_confirm` or `odoo_payment`, extract Odoo operation data from approval file body, call `odoo_mcp.py` with appropriate `--action` and `--data`. Wrap call with `retry_handler`. On failure, use `quarantine_utils` to quarantine task and create alert.
- [x] T013 [US1] Extend `orchestrator.py` — add Odoo draft saving: after Claude generates a plan with Odoo operation, save a local Markdown copy of the draft to `AI_Employee_Vault/Odoo_Drafts/` with invoice/payment details before creating the approval file. Per FR-005.
- [x] T014 [US1] Extend `orchestrator.py` — add Odoo rejection handling: when an Odoo approval file is moved to `Rejected/`, call `odoo_mcp.py --action cancel_invoice` (or equivalent) to cancel the draft in Odoo, log rejection with Odoo record ID.
- [x] T015 [US1] Integrate retry + quarantine for Odoo: wrap all `odoo_mcp.py` subprocess calls in `retry_handler`. On Odoo unreachable (ConnectionError, timeout), retry with backoff. After exhaustion, move task to `Quarantine/` and create alert in `Alerts/`. Per acceptance scenario 4.

**Checkpoint**: Odoo invoice/payment flow works end-to-end: file trigger → Claude plan → Odoo draft → local copy → HITL approval → Odoo confirm → Done/ with full logging. Test with `--dry-run` first.

---

## Phase 4: User Story 2 — Multi-Platform Social Media Posting & Summaries (Priority: P2)

**Goal**: Draft and post content to Facebook, Instagram, and X/Twitter after HITL approval. Fetch recent activity and generate engagement summaries.

**Independent Test**: Drop a file "Post about our new AI consulting service on all social platforms" into `watch_inbox/`. Verify: Claude drafts platform-specific posts, approval files created for each platform. Approve one (e.g., Facebook). Verify: post published via FB Graph API, recent activity fetched, social summary generated in `Briefings/`.

### Implementation for User Story 2

- [x] T016 [P] [US2] Create `social_facebook_mcp.py` — Facebook MCP server. CLI: `--action {post, fetch_activity}`, `--content <text>`, `--dry-run`. Use Facebook Graph API via `facebook-sdk` or `requests`. Post to page, fetch recent posts/likes/comments (last 7 days). Load `FB_PAGE_ACCESS_TOKEN` and `FB_PAGE_ID` from `.env`. Return JSON to stdout. Log via `log_utils`. Gold header. < 150 lines.
- [x] T017 [P] [US2] Create `social_instagram_mcp.py` — Instagram MCP server. CLI: `--action {post, fetch_activity}`, `--content <caption>`, `--media-url <url>`, `--dry-run`. Use Instagram Graph API via `requests`. Post to business account, fetch recent media/comments (last 7 days). Load `IG_ACCESS_TOKEN` and `IG_BUSINESS_ACCOUNT_ID` from `.env`. Return JSON to stdout. Log via `log_utils`. Gold header. < 150 lines.
- [x] T018 [P] [US2] Create `social_x_mcp.py` — X/Twitter MCP server. CLI: `--action {post, fetch_activity}`, `--content <text>`, `--dry-run`. Use Twitter API v2 via `tweepy` or `requests-oauthlib`. Post tweet (if paid tier available, else fallback to draft file in `Plans/` with manual note per FR-010). Fetch recent tweets/engagement (last 7 days). Load X API credentials from `.env`. Return JSON to stdout. Log via `log_utils`. Gold header. < 150 lines.
- [x] T019 [US2] Update `AI_Employee_Vault/agent_skills/social_post_skills.md` — expand from LinkedIn-only to multi-platform: add Facebook format rules (longer narrative), Instagram format rules (visual-caption style, hashtag-heavy), X/Twitter format rules (≤280 chars, concise). Keep LinkedIn rules. Add platform selection logic.
- [x] T020 [US2] Create `AI_Employee_Vault/agent_skills/social_summary_skills.md` — Agent Skill describing: how to aggregate engagement data across platforms, what metrics to highlight (likes, comments, shares, impressions), sentiment indicators, lead keyword detection, summary format for Briefings/. Per FR-031.
- [x] T021 [US2] Extend `orchestrator.py` — add social dispatch in `handle_approved()`: detect `action_type: post_facebook`, `post_instagram`, `post_x`. Extract post content from approval file body. Call appropriate `social_*_mcp.py` with `--action post --content <text>`. Wrap with `retry_handler`. On failure, quarantine + alert.
- [x] T022 [US2] Add social activity fetching to orchestrator: after a social post is successfully dispatched (or on a schedule), call each social MCP with `--action fetch_activity` and save the combined summary to `AI_Employee_Vault/Briefings/Social_Summary_<date>.md`. Log the fetch.

**Checkpoint**: Social posts can be drafted per-platform, approved via HITL, and published. Activity is fetched and summarized. Test with `--dry-run` for each platform.

---

## Phase 5: User Story 3 — Weekly Autonomous Audit & CEO Briefing (Priority: P3)

**Goal**: Every Sunday night (or manually), run a comprehensive audit across Odoo transactions, vault tasks, and social activity, producing a Monday Briefing with 5 mandatory sections.

**Independent Test**: Populate `Done/` with completed tasks. Ensure Odoo has transactions (or use `--dry-run` mock data). Trigger audit manually. Verify: `Briefings/Audit_YYYY-MM-DD.md` generated with Revenue Summary, Completed Tasks, Bottleneck Analysis, Social Activity Summary, Proactive Suggestions.

### Implementation for User Story 3

- [x] T023 [US3] Create `AI_Employee_Vault/agent_skills/audit_skills.md` — Agent Skill describing: revenue calculation rules (total invoiced, paid, outstanding from Odoo), task grouping by domain, bottleneck detection (longest-duration tasks, longest-waiting approvals), social metrics aggregation, suggestion templates. Per FR-032.
- [x] T024 [US3] Create `audit_generator.py` — Weekly audit script replacing/extending `briefing_generator.py`. CLI: `--dry-run`, `--generate-audit`. Reads: (1) Odoo transactions via `odoo_mcp.py --action list_invoices/list_payments`, (2) vault `Done/` tasks for past 7 days, (3) social summaries from `Briefings/Social_Summary_*.md`. Produces `Briefings/Audit_YYYY-MM-DD.md` with 5 sections per FR-017. Gold header. < 200 lines.
- [x] T025 [US3] Implement Revenue Summary section in `audit_generator.py`: parse Odoo invoice/payment data, calculate total invoiced, total paid, outstanding amounts. Handle zero-transactions case gracefully ("No transactions this period"). Per FR-018.
- [x] T026 [US3] Implement Bottleneck Analysis section in `audit_generator.py`: scan `Done/` tasks for duration (created → completed), scan `Pending_Approval/` for oldest waiting items, identify tasks exceeding expected duration thresholds.
- [x] T027 [US3] Update `orchestrator.py` — change `check_monday_briefing()` to `check_weekly_audit()`: trigger on Sunday night (weekday == 6) instead of Monday. Call `audit_generator.py` instead of `briefing_generator.py`. Also support `--generate-audit` CLI flag for manual trigger. Per FR-015.

**Checkpoint**: Weekly audit produces a comprehensive 5-section briefing. Can be triggered manually or auto-triggered on Sunday. Works with zero data gracefully.

---

## Phase 6: User Story 4 — Error Recovery & Watchdog Resilience (Priority: P4)

**Goal**: Handle API failures with retries, quarantine bad data, create alerts, and restart crashed processes automatically.

**Independent Test**: Start all watchers and orchestrator. Kill a watcher process. Verify: watchdog detects and restarts within 30 seconds. Simulate API 500 errors. Verify: retries with backoff, then quarantine + alert.

### Implementation for User Story 4

- [x] T028 [US4] Create `watchdog_monitor.py` — process monitor that checks if watcher/orchestrator processes are running (by PID file or process name). Polls every 15 seconds. If a monitored process is not running, restarts it via `subprocess.Popen`. Logs restart events. Creates alert in `Alerts/` if restart fails. CLI: `--dry-run`, `--processes <json-list>`. Gold header. < 150 lines.
- [x] T029 [US4] Integrate `retry_handler.py` into `email_mcp.py` — wrap Gmail API calls with retry handler for transient errors (HTTP 429, 500, 503). On exhaustion, return structured error JSON. Log each retry.
- [x] T030 [US4] Integrate `retry_handler.py` into `gmail_watcher.py` — wrap Gmail API poll calls with retry handler. On extended outage, log warning and continue polling (do not crash). Per FR-023 graceful degradation.
- [x] T031 [US4] Implement API-down queue behavior in `orchestrator.py` — when a domain's API is down (detected by consecutive quarantined tasks), stop processing new tasks for that domain (leave in `Needs_Action/`). Continue processing other domains. Resume automatically when the API responds successfully. Per acceptance scenario 4.
- [x] T032 [US4] Add PID file management to `filesystem_watcher.py`, `gmail_watcher.py`, and `orchestrator.py` — each writes a `.pid` file on startup, removes on clean shutdown. Watchdog uses these to detect crashes. Add signal handler for graceful shutdown.

**Checkpoint**: Watchdog monitors and restarts processes. Retries are integrated across all MCPs. Quarantine and alerts work for all failure scenarios.

---

## Phase 7: User Story 5 — Cross-Domain Multi-Step Task Completion (Priority: P5)

**Goal**: Handle complex tasks spanning Odoo + social + email via the Ralph Wiggum persistence loop with file-move completion checking.

**Independent Test**: Drop a file simulating a client invoice request. Verify the full chain: Odoo draft → approval → Odoo post → social post draft → approval → social post → all logged → reflected in next audit.

### Implementation for User Story 5

- [x] T033 [US5] Upgrade Ralph Wiggum loop in `orchestrator.py` `invoke_claude()` — replace promise-tag completion check with file-move check: after each iteration, verify if the task file has appeared in `Done/` (moved by orchestrator after all steps complete). Retain `TASK_COMPLETE` stdout check as secondary. Max 50 iterations (already set in T009). Per FR-024.
- [x] T034 [US5] Implement multi-step plan parsing in `orchestrator.py` — when Claude generates a plan with multiple sequential steps (Odoo + social), the orchestrator must: (1) execute steps in order, (2) create approval files for each HITL step, (3) wait for each approval before proceeding, (4) track step progress in the task frontmatter or a separate state file.
- [x] T035 [US5] Add hard-failure handling for Ralph Wiggum loop — when 50 iterations reached without completion: create alert in `Alerts/` with iteration count and last state, move task to `Quarantine/`, log hard failure. Per FR-025, acceptance scenario 2.
- [x] T036 [US5] Add iteration logging — each Ralph Wiggum iteration logs: iteration number, current state, elapsed time, what was attempted. Per FR-026.

**Checkpoint**: Multi-step tasks complete the full chain autonomously with HITL gates at each external action. Hard-failure at 50 iterations works correctly.

---

## Phase 8: User Story 6 — Documentation Artifacts (Priority: P6)

**Goal**: Generate `architecture.md` and `lessons_learned.md` as Gold completion deliverables.

**Independent Test**: After all Gold features work, trigger documentation generation. Verify: `architecture.md` has system diagram + component descriptions, `lessons_learned.md` has 5-10 insights.

### Implementation for User Story 6

- [x] T037 [P] [US6] Create `AI_Employee_Vault/architecture.md` — system diagram (Mermaid preferred, ASCII fallback) showing: all watchers (filesystem, gmail, odoo event, social activity), orchestrator, all MCPs (email, odoo, facebook, instagram, x), vault folder flow, HITL loop, watchdog, Ralph Wiggum loop. Component descriptions. Data flow annotations. Integration points. Per FR-034.
- [x] T038 [P] [US6] Create `AI_Employee_Vault/lessons_learned.md` — 5-10 key insights covering: what worked well (agent skills pattern, HITL folder workflow, incremental tier approach), what was challenging (API credential management, multi-step orchestration, rate limits), decisions that would be made differently, recommendations for Platinum Tier. Per FR-035.

**Checkpoint**: Documentation artifacts exist and are comprehensive. System diagram accurately reflects the implemented architecture.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, Dashboard update, and end-to-end verification.

- [x] T039 Update `AI_Employee_Vault/Dashboard.md` — add Gold fields: Odoo balance snapshot, pending approvals count by domain, last audit date, social post counts, system health (watchdog status). Per FR-039.
- [x] T040 Update all existing Python files — change header comments from `# Silver Tier` to `# Gold Tier – Hackathon 0 – Personal AI Employee`. Verify all scripts support `--dry-run`.
- [x] T041 Verify HITL enforcement — audit all code paths to confirm zero bypass paths for: `odoo_confirm`, `odoo_payment`, `post_facebook`, `post_instagram`, `post_x`, `email_send`. Per SC-007.
- [x] T042 End-to-end cross-domain smoke test — manually walk through: file drop "Invoice Client X, PKR 50K, then announce on social media" → Odoo draft → approve → Odoo post → social drafts → approve FB → post → fetch activity → verify audit includes all. Per SC-010.
- [x] T043 Write `GOLD TIER AUTONOMOUS EMPLOYEE COMPLETE – READY FOR PLATINUM OR SUBMISSION` marker after all tasks verified.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 Odoo (Phase 3)**: Depends on Foundational phase completion
- **US2 Social (Phase 4)**: Depends on Foundational phase completion. Can run in parallel with US1.
- **US3 Audit (Phase 5)**: Depends on US1 (Odoo data) and US2 (social data) for meaningful output. Can start after Phase 2 with mock data.
- **US4 Resilience (Phase 6)**: Depends on Foundational (T004 retry_handler). Best done after US1+US2 exist so retry can be integrated.
- **US5 Cross-Domain (Phase 7)**: Depends on US1 + US2 being functional (needs both Odoo and social MCPs)
- **US6 Docs (Phase 8)**: Depends on all other stories being complete (documents final architecture)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no other story dependency. **MVP target.**
- **US2 (P2)**: After Foundational — independent of US1, can run in parallel
- **US3 (P3)**: Soft dependency on US1 + US2 (needs Odoo/social data for real audit)
- **US4 (P4)**: After Foundational — integrates into US1/US2 MCPs
- **US5 (P5)**: Hard dependency on US1 + US2 (multi-step spans both domains)
- **US6 (P6)**: After all other stories complete

### Within Each User Story

- Agent Skills (`.md`) before MCP scripts (`.py`) — Claude reads skills during plan generation
- MCP scripts before orchestrator integration — MCP must exist to be called
- Orchestrator dispatch before approval handling — dispatch enables HITL
- Core flow before error handling — get the happy path working first

### Parallel Opportunities

- T002, T003 (Phase 1): Different files, no dependencies
- T005, T006, T007 (Phase 2): Different files, independent utilities
- T016, T017, T018 (Phase 4): Three social MCPs are independent of each other
- T037, T038 (Phase 8): Documentation files are independent
- US1 and US2 (Phases 3-4): Can run in parallel since they target different APIs

---

## Parallel Example: User Story 2 (Social MCPs)

```bash
# Launch all three social MCPs in parallel (different files, no dependencies):
Task: "Create social_facebook_mcp.py"   # T016
Task: "Create social_instagram_mcp.py"  # T017
Task: "Create social_x_mcp.py"         # T018
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009)
3. Complete Phase 3: User Story 1 — Odoo (T010-T015)
4. **STOP and VALIDATE**: Test Odoo invoice flow end-to-end with `--dry-run`
5. This alone demonstrates Gold-level ERP capability

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 Odoo → Test independently → **MVP demo** (invoice flow)
3. Add US2 Social → Test independently → Multi-platform posting works
4. Add US3 Audit → Test independently → Weekly intelligence report
5. Add US4 Resilience → Test independently → Production-grade error handling
6. Add US5 Cross-Domain → Test independently → Full autonomous chain
7. Add US6 Docs → Generate artifacts → Gold complete
8. Polish → Final verification → Write completion marker

### Recommended Build Order (Sequential)

Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 6 (US4, resilience) → Phase 5 (US3, audit) → Phase 7 (US5, cross-domain) → Phase 8 (US6, docs) → Phase 9 (polish)

*Note: US4 (resilience) is moved before US3 (audit) because retry/watchdog patterns should be in place before the audit generator calls multiple APIs.*

---

## Summary

- **Total tasks**: 43
- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 6 tasks
- **Phase 3 (US1 Odoo)**: 6 tasks
- **Phase 4 (US2 Social)**: 7 tasks
- **Phase 5 (US3 Audit)**: 5 tasks
- **Phase 6 (US4 Resilience)**: 5 tasks
- **Phase 7 (US5 Cross-Domain)**: 4 tasks
- **Phase 8 (US6 Docs)**: 2 tasks
- **Phase 9 (Polish)**: 5 tasks
- **Parallel opportunities**: 10 tasks marked [P], plus US1/US2 phases can run in parallel
- **MVP scope**: Phases 1-3 (15 tasks → working Odoo invoice flow)
