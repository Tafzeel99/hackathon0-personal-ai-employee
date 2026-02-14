# Feature Specification: Gold Tier Autonomous Employee

**Feature Branch**: `003-gold-tier-autonomous-employee`
**Created**: 2026-02-14
**Status**: Draft
**Input**: User description: "Elevate Silver Tier into a truly autonomous digital employee with ERP accounting (Odoo), multi-platform social media (FB/IG/X), weekly autonomous audit, production-grade resilience, and comprehensive audit trail."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Odoo ERP Invoice & Payment Flow (Priority: P1)

As a business owner, I want the AI employee to draft invoices and payments in my self-hosted Odoo system when triggered by an incoming email or file request, so that routine accounting tasks are handled automatically while I retain approval authority over actual postings.

**Why this priority**: Accounting is the highest-value Gold capability. Without Odoo integration, Gold Tier is just Silver with more social media. This story delivers real business value by automating the most time-consuming routine accounting operation.

**Independent Test**: Drop a file "Create invoice for Client X, PKR 50,000 for consulting services" into watch_inbox/. Verify: orchestrator invokes Claude, Claude drafts invoice via Odoo MCP (JSON-RPC to local Odoo), approval file appears in Pending_Approval/ with invoice details. Move to Approved/. Verify Odoo invoice is confirmed, vault log records the full chain, and a local copy exists in Odoo_Drafts/.

**Acceptance Scenarios**:

1. **Given** Odoo Community is running locally and a file requesting an invoice is dropped into watch_inbox/, **When** the orchestrator processes it, **Then** a draft invoice is created in Odoo via JSON-RPC, a local copy is saved to Odoo_Drafts/, and an approval file is created in Pending_Approval/ with action_type: odoo_confirm
2. **Given** an Odoo invoice approval file exists in Approved/, **When** the orchestrator detects it, **Then** the invoice is confirmed/posted in Odoo via MCP, the result is logged with Odoo record ID, and the task moves to Done/
3. **Given** an Odoo invoice approval file is moved to Rejected/, **When** the orchestrator detects it, **Then** the draft is cancelled in Odoo, rejection is logged, and the task moves to Done/ with status: rejected
4. **Given** Odoo is unreachable, **When** the MCP attempts a JSON-RPC call, **Then** the system retries with exponential backoff (1s, 2s, 4s, max 60s, 3 attempts), and if still failing, moves the task to Quarantine/ and creates an alert in Alerts/

---

### User Story 2 - Multi-Platform Social Media Posting & Summaries (Priority: P2)

As a business owner, I want the AI employee to draft and post content to Facebook, Instagram, and X/Twitter on my behalf (after my approval), and fetch recent activity from these platforms to generate engagement summaries, so that I maintain an active social presence without manual effort.

**Why this priority**: Social media management is the second-highest value Gold capability. It directly extends Silver's LinkedIn drafting to full multi-platform coverage and adds the unique "fetch + summarize" intelligence layer.

**Independent Test**: Drop a file "Post about our new AI consulting service on all social platforms" into watch_inbox/. Verify: Claude drafts platform-specific posts (different tone/length per platform), approval files are created for each platform. Approve one (e.g., Facebook). Verify: post is published via FB Graph API, recent activity is fetched, and a social summary is generated in Briefings/.

**Acceptance Scenarios**:

1. **Given** a task requesting a social media post is in Needs_Action/, **When** the orchestrator processes it, **Then** Claude generates platform-specific drafts for FB, IG, and X, each with appropriate format (IG: visual-focused caption, X: under 280 chars, FB: longer narrative), and creates separate approval files for each platform
2. **Given** a Facebook post approval is in Approved/, **When** the orchestrator dispatches it, **Then** the social_facebook_mcp.py posts via Graph API, logs the post ID, and returns a JSON result
3. **Given** an X/Twitter post fails due to paid-tier API restriction, **When** the MCP encounters the error, **Then** it falls back to creating a draft file in Plans/ with the post text and a note "Manual posting required — X API paid tier not available", and logs the fallback
4. **Given** social posts have been made in the last 7 days, **When** the social summary is triggered, **Then** the system fetches recent activity from each platform (likes, comments, shares, impressions where available) and Claude generates a summary with engagement metrics, sentiment indicators, and lead keyword detection

---

### User Story 3 - Weekly Autonomous Audit & CEO Briefing (Priority: P3)

As a CEO, I want the system to autonomously run a comprehensive weekly audit every Sunday night that reviews all Odoo transactions, completed vault tasks, and social activity, producing a detailed Monday Briefing with revenue calculations, bottleneck analysis, and proactive suggestions.

**Why this priority**: The audit is the "intelligence crown jewel" of Gold — it ties all domains together (ERP + vault + social) into a single executive summary. It depends on US1 and US2 being functional to produce meaningful data, making it naturally P3.

**Independent Test**: Populate Done/ with several completed tasks across domains (email, Odoo, social). Ensure Odoo has some transactions. Trigger the audit manually (or simulate Sunday). Verify: Briefings/Audit_YYYY-MM-DD.md is generated with all 5 required sections (Revenue Summary, Completed Tasks, Bottleneck Analysis, Social Activity Summary, Proactive Suggestions).

**Acceptance Scenarios**:

1. **Given** it is Sunday night (or the audit is triggered manually), **When** the audit generator runs, **Then** it reads Odoo transactions for the past 7 days, scans vault Done/ tasks, and fetches social summaries
2. **Given** audit data is collected, **When** Claude generates the briefing, **Then** the Briefings/Audit_YYYY-MM-DD.md file contains: Revenue Summary (total invoiced, total paid, outstanding from Odoo), Completed Tasks (grouped by domain), Bottleneck Analysis (tasks exceeding expected duration, approvals waiting longest), Social Activity Summary (posts made, engagement metrics), and Proactive Suggestions (data-driven recommendations)
3. **Given** the briefing is generated, **When** it is written to the vault, **Then** a log entry with action=audit_generated is created with task_count, revenue_total, and output path in details

---

### User Story 4 - Error Recovery & Watchdog Resilience (Priority: P4)

As a system operator, I want the AI employee to handle API failures gracefully — retrying transient errors, quarantining bad data, creating human-readable alerts for critical failures, and automatically restarting crashed processes — so that the system runs reliably without constant monitoring.

**Why this priority**: Resilience is essential for a system that claims "autonomous employee" status but is a cross-cutting concern, not a standalone feature. It builds on US1-US3 patterns and hardens them.

**Independent Test**: Start all watchers and orchestrator. Kill a watcher process. Verify: watchdog detects the stopped process within 30 seconds and restarts it. Simulate an API returning 500 errors. Verify: retries with backoff, then quarantine + alert.

**Acceptance Scenarios**:

1. **Given** a watcher or orchestrator process crashes, **When** the watchdog detects the process is not running, **Then** it restarts the process within 30 seconds and logs the restart event
2. **Given** an MCP call returns a transient error (HTTP 429, 500, 503), **When** the retry handler processes it, **Then** it retries with exponential backoff (1s, 2s, 4s, max 60s) up to 3 times, logging each retry
3. **Given** a task fails after all retries are exhausted, **When** the retry handler gives up, **Then** the task file is moved to Quarantine/ with error details added to frontmatter, and an alert file is created in Alerts/ with a human-readable description and suggested remediation
4. **Given** an external API is down for an extended period, **When** tasks for that domain continue arriving, **Then** they are queued in Needs_Action/ (not processed), and when the API recovers, normal processing resumes automatically

---

### User Story 5 - Cross-Domain Multi-Step Task Completion (Priority: P5)

As a business owner, I want the system to handle complex multi-step tasks that span multiple domains — for example, an invoice request arriving via email that gets processed through Odoo, triggers a social media announcement after posting, and is reflected in the weekly audit — completing the entire chain autonomously via the Ralph Wiggum persistence loop.

**Why this priority**: This is the "demo story" that proves Gold Tier works end-to-end across all domains. It depends on all previous stories being functional.

**Independent Test**: Drop a file simulating a client invoice request. Verify the full chain: Odoo draft → approval → Odoo post → social post draft → approval → social post → all logged → reflected in next audit.

**Acceptance Scenarios**:

1. **Given** a multi-step task requiring Odoo + social actions is dropped as a file, **When** the orchestrator processes it via the Ralph Wiggum loop, **Then** each step is completed sequentially (Odoo draft → approval wait → Odoo post → social draft → approval wait → social post) with file-move completion checks between steps
2. **Given** the Ralph Wiggum loop is running a complex task, **When** it reaches 50 iterations without TASK_COMPLETE or the task appearing in Done/, **Then** it creates an alert file in Alerts/, moves the task to Quarantine/, and logs a hard failure
3. **Given** a multi-step task completes successfully, **When** all steps are done, **Then** comprehensive logs exist for every step allowing full reconstruction of the action chain from trigger to final completion

---

### User Story 6 - Documentation Artifacts (Priority: P6)

As a project stakeholder, I want the system to generate architecture.md (with a system diagram) and lessons_learned.md at Gold completion, so that the project is self-documenting and ready for Platinum planning.

**Why this priority**: Documentation is a Gold completion requirement but has no runtime dependencies — it can be generated at the very end after everything else works.

**Independent Test**: After all Gold features are working, trigger documentation generation. Verify: architecture.md contains an ASCII/Mermaid diagram showing all components and data flows, lessons_learned.md contains 5-10 substantive insights.

**Acceptance Scenarios**:

1. **Given** all Gold Tier features are implemented and tested, **When** documentation generation is triggered, **Then** AI_Employee_Vault/architecture.md is created with a system diagram (ASCII art or Mermaid), component descriptions, data flow between watchers → orchestrator → MCPs → vault, and integration points (Odoo, Gmail, FB, IG, X)
2. **Given** all Gold Tier features are complete, **When** lessons_learned.md generation is triggered, **Then** AI_Employee_Vault/lessons_learned.md is created with 5-10 key insights covering what worked, what didn't, decisions that would be made differently, and recommendations for Platinum

---

### Edge Cases

- What happens when Odoo credentials expire mid-operation? System MUST detect auth failure, create an alert, and not retry indefinitely.
- What happens when a social platform rate-limits the fetch-activity call? System MUST respect rate limits, log the event, and retry after the cooldown window.
- What happens when a multi-step task's approval is rejected partway through (e.g., Odoo posted but social post rejected)? Each step MUST be independently completable; partial completion is logged, and remaining steps are cancelled gracefully.
- What happens when the vault runs out of disk space? System MUST detect write failures, create a console warning, and stop processing new tasks rather than corrupting files.
- What happens when two tasks attempt to create the same Odoo partner simultaneously? Claim-by-move MUST ensure only one task per domain is active, preventing race conditions.
- What happens when the weekly audit runs but Odoo has zero transactions? System MUST still generate a valid briefing with "No transactions this period" rather than failing.

## Requirements *(mandatory)*

### Functional Requirements

**Odoo Integration**:
- **FR-001**: System MUST connect to a self-hosted Odoo Community 19+ instance via JSON-RPC external API
- **FR-002**: System MUST create draft invoices in Odoo with partner, product lines, amounts, and reference fields
- **FR-003**: System MUST create draft payments in Odoo linked to existing invoices
- **FR-004**: System MUST confirm/post Odoo invoices and payments ONLY after HITL approval
- **FR-005**: System MUST save a local Markdown copy of each Odoo draft in Odoo_Drafts/ for human review
- **FR-006**: System MUST read Odoo transactions (invoices, payments) for use in weekly audit
- **FR-007**: All Odoo credentials MUST be stored in .env and never committed to version control

**Social Media MCPs**:
- **FR-008**: System MUST post content to Facebook pages via Graph API
- **FR-009**: System MUST post content to Instagram Business accounts via Instagram API
- **FR-010**: System MUST post content to X/Twitter via API v2; if posting requires a paid tier not available, system MUST fallback to creating a draft file
- **FR-011**: System MUST fetch recent activity (last 7 days) from each social platform: posts, likes, comments, shares/retweets where available
- **FR-012**: System MUST generate platform-specific post formats (X: ≤280 chars; IG: visual-caption style; FB: longer narrative)
- **FR-013**: All social posts MUST go through HITL approval before publishing
- **FR-014**: System MUST generate social activity summaries with engagement metrics and sentiment indicators

**Weekly Audit**:
- **FR-015**: System MUST trigger a weekly audit on Sunday night (or via manual --generate-audit flag)
- **FR-016**: Audit MUST read Odoo transactions, vault Done/ tasks, and social summaries for the past 7 days
- **FR-017**: Audit briefing MUST include: Revenue Summary, Completed Tasks by Domain, Bottleneck Analysis, Social Activity Summary, and Proactive Suggestions
- **FR-018**: Revenue Summary MUST include total invoiced, total paid, and outstanding amounts from Odoo

**Error Recovery & Resilience**:
- **FR-019**: System MUST retry transient API errors with exponential backoff (1s, 2s, 4s, max 60s, max 3 retries)
- **FR-020**: System MUST move tasks to Quarantine/ after retry exhaustion with error details in frontmatter
- **FR-021**: System MUST create alert files in Alerts/ for critical failures (auth expired, API down, process crash)
- **FR-022**: A watchdog process MUST monitor all watcher and orchestrator processes and restart them if they crash
- **FR-023**: System MUST support graceful degradation: if one API is down, other domains MUST continue operating

**Ralph Wiggum Loop**:
- **FR-024**: Ralph Wiggum loop MUST use file-move completion check (task in Done/ signals finish) as preferred method
- **FR-025**: Maximum 50 iterations per task; after limit, create alert in Alerts/ and move task to Quarantine/
- **FR-026**: Each iteration MUST be logged with iteration count and current state

**Logging**:
- **FR-027**: All log entries MUST include: timestamp, action, source, result, task_ref, and details
- **FR-028**: Log details MUST include MCP call parameters, response snippets, Odoo record IDs, social post IDs, and retry counts where applicable
- **FR-029**: Logs MUST be append-only JSONL format, one file per day, allowing full reconstruction of any action sequence

**Agent Skills**:
- **FR-030**: System MUST include odoo_skills.md with invoice/payment draft patterns and validation rules
- **FR-031**: System MUST include social_summary_skills.md with multi-platform analysis rules
- **FR-032**: System MUST include audit_skills.md with revenue calculation, bottleneck detection, and suggestion templates
- **FR-033**: System MUST include recovery_skills.md with retry, quarantine, and alert patterns

**Documentation**:
- **FR-034**: System MUST generate architecture.md with a system diagram (ASCII or Mermaid) at Gold completion
- **FR-035**: System MUST generate lessons_learned.md with 5-10 key insights at Gold completion

**Vault Extensions**:
- **FR-036**: System MUST create and maintain Quarantine/ folder for failed tasks
- **FR-037**: System MUST create and maintain Alerts/ folder for critical failure notifications
- **FR-038**: System MUST create and maintain Odoo_Drafts/ folder for local copies of Odoo drafts
- **FR-039**: Dashboard.md MUST be updated to include Odoo balance snapshot, pending approvals count, and last audit date

### Key Entities

- **Odoo Invoice Draft**: A draft invoice created in Odoo via JSON-RPC. Contains partner, product lines, amounts, reference. Local copy saved as Markdown in Odoo_Drafts/.
- **Odoo Payment Draft**: A draft payment linked to an invoice in Odoo. Contains partner, amount, journal. Requires HITL to post.
- **Social Post**: Content formatted for a specific platform (FB/IG/X). Contains text, optional media reference, hashtags. Goes through HITL before publishing.
- **Social Activity Summary**: Aggregated engagement data from one or more platforms over a period. Contains metrics (likes, comments, shares), sentiment indicators, and lead keywords.
- **Audit Briefing**: Comprehensive weekly report combining Odoo financials, vault task completions, and social activity. Five mandatory sections.
- **Quarantined Task**: A task that failed after retry exhaustion. Contains original task data plus error details and timestamp of quarantine.
- **Alert File**: A human-readable notification of a critical failure. Contains error description, affected component, and suggested remediation steps.

### Assumptions

- Odoo Community 19+ is installed and accessible locally (Docker or VM) with JSON-RPC enabled on the default port
- Facebook Page access token and Instagram Business account are configured with appropriate permissions
- X/Twitter API v2 credentials are available (free tier at minimum; posting may require paid Basic tier)
- The user has configured all API credentials in .env before running Gold Tier scripts
- The same HITL folder-based pattern from Silver works for all new action types (Odoo confirm, social post)
- Social platform APIs allow fetching engagement data for owned posts without additional premium access

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A triggered invoice request completes the full chain (draft → approval → Odoo post) within 5 minutes of human approval
- **SC-002**: Social posts are published to at least 3 platforms (FB, IG, X or draft-fallback) from a single task request
- **SC-003**: Social activity summaries cover the last 7 days and include engagement metrics from all active platforms
- **SC-004**: Weekly audit briefing is generated autonomously and contains revenue figures matching Odoo data within the reporting period
- **SC-005**: Transient API failures (simulated) are retried up to 3 times with increasing delay before quarantine
- **SC-006**: A crashed watcher process is detected and restarted by the watchdog within 30 seconds
- **SC-007**: All external actions (Odoo confirm, social post, email send) require and enforce HITL approval — zero bypass paths
- **SC-008**: Any action can be fully reconstructed from log entries alone (timestamp, prompt, MCP params, outcome)
- **SC-009**: Architecture documentation includes a visual system diagram showing all components and their data flows
- **SC-010**: End-to-end cross-domain demo completes: file trigger → Odoo invoice → social post → audit reflection, all logged
- **SC-011**: Multi-step tasks complete via Ralph Wiggum loop with file-move completion checking, within 50 iterations
