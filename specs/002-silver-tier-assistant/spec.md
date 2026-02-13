# Feature Specification: Silver Tier Functional Assistant

**Feature Branch**: `002-silver-tier-assistant`
**Created**: 2026-02-13
**Status**: Draft
**Input**: User description: "Transform Bronze Tier skeleton into functional assistant with Gmail watcher, email MCP, HITL approval workflow, LinkedIn post drafting, and scheduled CEO Briefing"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gmail Watcher Detects Incoming Email (Priority: P1)

As a business owner, I want incoming Gmail messages to automatically create task
files in my vault so that I never miss an actionable email and can process them
through my AI assistant workflow.

**Why this priority**: Without a second input channel beyond file drops, the
system cannot be "proactive." Gmail is the most common business communication
channel. This is the foundational new capability that differentiates Silver
from Bronze.

**Independent Test**: Start the Gmail watcher with valid OAuth credentials.
Send a test email to the monitored inbox. Within 120 seconds, confirm a new
`Needs_Action/EMAIL_*.md` file appears with correct frontmatter (type, sender,
subject, snippet) and body content.

**Acceptance Scenarios**:

1. **Given** the Gmail watcher is running and authenticated, **When** a new
   unread email arrives in the inbox, **Then** the watcher creates
   `Needs_Action/EMAIL_<timestamp>_<subject_slug>.md` with frontmatter
   containing `type: email_inbound`, sender, subject, snippet, and body.
2. **Given** the Gmail watcher has processed an email, **When** it marks the
   email as read, **Then** subsequent polling cycles do not create duplicate
   task files for the same email.
3. **Given** Gmail API credentials are missing or expired, **When** the watcher
   attempts to poll, **Then** it logs a clear error message and retries on
   the next polling cycle without crashing.
4. **Given** the inbox contains no new unread emails, **When** the watcher
   polls, **Then** it logs a "no new messages" status and continues polling.

---

### User Story 2 - Orchestrator Claims and Processes Tasks with HITL (Priority: P2)

As a business owner, I want an orchestrator script that automatically picks up
tasks, invokes Claude Code for reasoning, and routes external actions through
an approval workflow so that I maintain control over what the AI does externally
while still benefiting from its autonomous reasoning.

**Why this priority**: The orchestrator is the central nervous system. Without
it, watchers create task files that sit unprocessed. It connects detection
(watchers) to reasoning (Claude) to action (MCP). HITL is non-negotiable for
Silver safety guarantees.

**Independent Test**: Place a task file in `Needs_Action/`. Run the orchestrator.
Confirm it moves the file to `In_Progress/`, invokes Claude Code, generates a
Plan.md, and (if HITL needed) creates an approval file in `Pending_Approval/`.
Then move the approval to `Approved/` and confirm the orchestrator detects it.

**Acceptance Scenarios**:

1. **Given** a task file exists in `Needs_Action/`, **When** the orchestrator
   runs, **Then** it moves the file to `In_Progress/` (claim-by-move) and
   invokes Claude Code with the task content and relevant Agent Skills.
2. **Given** Claude generates a Plan.md that identifies an external action,
   **When** the plan contains `action_required: yes`, **Then** the orchestrator
   creates an approval request file in `Pending_Approval/` with action type,
   target, and content preview.
3. **Given** a task does not require external action, **When** Claude completes
   the plan, **Then** the orchestrator moves the task and plan to `Done/`
   without creating an approval file.
4. **Given** two tasks exist in `Needs_Action/` simultaneously, **When** the
   orchestrator runs, **Then** it claims and processes them sequentially
   (one at a time) to prevent conflicts.
5. **Given** Claude does not produce a `TASK_COMPLETE` marker, **When** the
   Ralph Wiggum loop reaches 20 iterations, **Then** the orchestrator logs
   a warning, marks the task as incomplete, and moves on.

---

### User Story 3 - Email Send/Draft via MCP After Approval (Priority: P3)

As a business owner, I want to approve an email action by moving a file to the
`Approved/` folder, after which the system automatically sends or drafts the
email via Gmail, so that I can authorize external actions with a simple file
operation.

**Why this priority**: This completes the full email loop — from detection
(US1) through reasoning (US2) to execution. It is the first external action
the system performs and validates the entire HITL safety model.

**Independent Test**: Place a pre-formatted approval file in `Approved/` with
email send details. Run the orchestrator. Confirm the email MCP sends (or
drafts in dry-run mode) the email, logs the result, and moves the approval
file to `Done/`.

**Acceptance Scenarios**:

1. **Given** an approval file exists in `Approved/` with `hitl_type: email_send`,
   **When** the orchestrator detects it, **Then** it calls the email MCP to
   send (or draft) the email using the details in the approval file.
2. **Given** the email MCP is in dry-run mode, **When** an email send is
   triggered, **Then** the MCP logs the email details without actually sending
   and writes a dry-run result to the log.
3. **Given** a human moves an approval file to `Rejected/`, **When** the
   orchestrator detects it, **Then** it logs the rejection with reason
   (if provided), marks the task as `status: rejected`, and moves it to `Done/`.
4. **Given** the email MCP encounters an API error, **When** it fails to send,
   **Then** it logs the error with details, does NOT move the approval file to
   `Done/`, and alerts via a log entry so the human can retry.

---

### User Story 4 - LinkedIn Post Drafting (Priority: P4)

As a business owner, I want the AI to draft LinkedIn posts based on task context
(e.g., a sales lead, a milestone, a thought leadership topic) and present them
for my approval before posting, so that I maintain my professional voice while
saving time on content creation.

**Why this priority**: Extends the system's usefulness beyond email into social
media. Demonstrates the HITL pattern works for multiple action types. LinkedIn
is the primary professional network for business owners in Karachi/Pakistan.

**Independent Test**: Drop a file in `watch_inbox/` with content like "Draft a
LinkedIn post about our new AI automation service." Process through the
orchestrator. Confirm the Plan.md contains a LinkedIn post draft and an approval
file is created in `Pending_Approval/` with the draft content.

**Acceptance Scenarios**:

1. **Given** a task mentions social media or LinkedIn posting, **When** Claude
   processes it using `social_post_skills.md`, **Then** the Plan.md includes
   a "LinkedIn Post Draft" section with professional tone, appropriate length
   (100-300 words), and a call-to-action.
2. **Given** a LinkedIn post draft is approved, **When** the approval file is
   moved to `Approved/`, **Then** the system logs the approved content for
   manual posting (or via API if available) and moves to `Done/`.
3. **Given** the task context is unrelated to social media, **When** Claude
   processes it, **Then** no LinkedIn draft is generated and no social media
   approval file is created.

---

### User Story 5 - Weekly CEO Briefing (Priority: P5)

As a business owner, I want a weekly summary briefing generated automatically
from completed tasks and logs so that I have a clear overview of what my AI
assistant accomplished, what is pending, and what to focus on next week.

**Why this priority**: This is the scheduling capability. It turns the system
from reactive (responds to inputs) to proactive (generates insights on a
cadence). It is lower priority because it does not block the core
detect-reason-act loop.

**Independent Test**: Place several completed task files in `Done/` with
various dates. Trigger the briefing generation manually (or wait for the
schedule). Confirm `Briefings/Monday_YYYY-MM-DD.md` appears with a summary
of completed tasks, pending items, and one proactive suggestion.

**Acceptance Scenarios**:

1. **Given** completed tasks exist in `Done/` from the past 7 days, **When**
   the briefing generator runs (manually or on schedule), **Then** it creates
   `Briefings/Monday_YYYY-MM-DD.md` with sections: Completed Tasks Summary,
   Pending Items, and one Proactive Suggestion.
2. **Given** no tasks were completed in the past 7 days, **When** the briefing
   generator runs, **Then** it creates a briefing noting "No tasks completed
   this week" and lists any pending items.
3. **Given** the briefing generator is configured for weekly schedule, **When**
   the scheduled time arrives (e.g., Monday 8:00 AM), **Then** the briefing
   is generated automatically without human intervention.

---

### Edge Cases

- What happens when two orchestrator instances run simultaneously? Only one
  MUST claim a task (file claim-by-move ensures atomic claim).
- What happens when the Gmail API rate limit is hit? The watcher MUST log
  the rate limit error and back off (double the polling interval temporarily).
- What happens when a file in `Pending_Approval/` sits for over 24 hours?
  The system MUST NOT auto-approve; it logs a reminder but takes no action.
- What happens when the vault disk is full? Watchers and orchestrator MUST
  log the error and halt gracefully rather than corrupting files.
- What happens when the orchestrator crashes mid-task? The task remains in
  `In_Progress/` and is NOT re-claimed until manually moved back to
  `Needs_Action/` by the human.
- What happens when an email has no subject or body? The Gmail watcher MUST
  still create a task file with `subject: (no subject)` and empty body.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST run two concurrent watchers: a filesystem watcher
  (polling `watch_inbox/` every 15 seconds) and a Gmail watcher (polling
  inbox every 120 seconds via OAuth).
- **FR-002**: Gmail watcher MUST create task files in `Needs_Action/` with
  frontmatter fields: `type: email_inbound`, `created`, `status: pending`,
  `priority`, `source`, `action_required`, `hitl_type`, plus email-specific
  fields (`from`, `subject`, `message_id`).
- **FR-003**: Filesystem watcher MUST continue to function as in Bronze Tier
  (detect `.txt`/`.md` drops in `watch_inbox/`, create `TASK_*.md` in
  `Needs_Action/`).
- **FR-004**: Orchestrator MUST claim tasks by moving files from `Needs_Action/`
  to `In_Progress/` before processing (file claim-by-move pattern).
- **FR-005**: Orchestrator MUST invoke Claude Code CLI with task content,
  relevant Agent Skills files, and vault context to generate Plan.md files.
- **FR-006**: Orchestrator MUST implement a Ralph Wiggum loop (re-invoke
  Claude up to 20 iterations) for multi-step tasks, checking for
  `TASK_COMPLETE` marker or file in `Done/` after each iteration.
- **FR-007**: When a plan identifies an external action (`action_required: yes`),
  the system MUST create an approval request file in `Pending_Approval/` with
  action type, target, content preview, and plan reference.
- **FR-008**: The system MUST poll `Approved/` for human-approved actions and
  execute them via the appropriate MCP (email send/draft).
- **FR-009**: The system MUST poll `Rejected/` for human-rejected actions, log
  the rejection, and move the task to `Done/` with `status: rejected`.
- **FR-010**: Email MCP MUST support sending and drafting Gmail messages using
  Google API OAuth credentials from `.env`.
- **FR-011**: Email MCP MUST support a dry-run mode that logs actions without
  sending real emails.
- **FR-012**: All actions (watcher detections, orchestrator claims, Claude
  invocations, HITL decisions, MCP executions) MUST be logged as structured
  JSON entries in `Logs/YYYY-MM-DD.json` with fields: `timestamp`, `action`,
  `source`, `task_ref`, `result`.
- **FR-013**: Agent Skills MUST be expanded with `email_skills.md` (email
  handling rules), `approval_skills.md` (HITL thresholds), and
  `social_post_skills.md` (LinkedIn drafting guidelines).
- **FR-014**: LinkedIn post drafting MUST be triggered by task context (Claude
  identifies when a post is appropriate using `social_post_skills.md`) and
  the draft MUST appear in the Plan.md with an approval request in
  `Pending_Approval/`.
- **FR-015**: System MUST generate a weekly CEO Briefing in
  `Briefings/Monday_YYYY-MM-DD.md` summarizing completed tasks, pending
  items, and one proactive suggestion.
- **FR-016**: All new Python scripts MUST include a `--dry-run` flag that
  prevents any external side effects.
- **FR-017**: Dashboard.md MUST be updated to show the count of files in
  `Pending_Approval/` and a link to the most recent briefing.
- **FR-018**: No external action (email send, post draft) MUST execute
  without a corresponding file having been moved to `Approved/` by a human.

### Key Entities

- **Task File**: A Markdown file with YAML frontmatter representing a unit
  of work. Created by watchers. Extended in Silver with `action_required`
  and `hitl_type` fields. Lifecycle: `Needs_Action/` → `In_Progress/` →
  `Done/` (or via `Pending_Approval/` → `Approved/`/`Rejected/`).
- **Approval Request**: A Markdown file in `Pending_Approval/` containing
  action type (`email_send`, `post_linkedin`), target (recipient/platform),
  content preview (email body or post draft), and reference to the
  originating plan. Created by orchestrator, moved by human.
- **Plan File**: A Markdown file in `Plans/` with objective, steps, status,
  and (Silver addition) an optional "Approval Required" section when
  external action is needed.
- **Log Entry**: A JSON object appended to `Logs/YYYY-MM-DD.json` (JSONL
  format) with timestamp, action type, source, task reference, and result.
- **Briefing**: A Markdown file in `Briefings/` summarizing the week's
  completed tasks, pending items, and a proactive suggestion. Generated
  on schedule.
- **Agent Skill**: A Markdown file in `agent_skills/` encoding Claude
  behavior rules for a specific capability (planning, email, approval
  routing, social posting).

### Assumptions

- User has a Google Cloud project with Gmail API enabled and OAuth
  credentials configured (setup instructions provided in code comments).
- The monitored Gmail inbox is a personal/business inbox (not a shared
  mailbox with complex routing rules).
- LinkedIn posting is draft-only in Silver (manual copy-paste or simple
  API if available); full API integration deferred to Gold.
- The "weekly" schedule for CEO Briefing is configurable but defaults to
  Monday generation covering the prior 7 days.
- The orchestrator runs as a long-lived process on the user's local machine
  (not deployed to cloud).
- `python-dotenv` or `os.environ` is available for loading `.env` secrets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Gmail watcher detects and creates task files for 100% of
  unread emails within 2 polling cycles (under 4 minutes).
- **SC-002**: Filesystem watcher (from Bronze) continues to detect and
  create task files for file drops within one polling cycle (under 15
  seconds).
- **SC-003**: Orchestrator processes a task from `Needs_Action/` to
  `Done/` (without HITL) in under 5 minutes including Claude reasoning
  time.
- **SC-004**: End-to-end HITL flow (task → plan → approval → execution →
  done) completes within 2 minutes of human moving the approval file
  (excluding human decision time).
- **SC-005**: Zero external actions (email send, LinkedIn post) execute
  without a corresponding file in `Approved/`.
- **SC-006**: All system events are captured in structured JSON logs with
  no gaps (every watcher detection, orchestrator claim, Claude call, HITL
  decision, and MCP execution is logged).
- **SC-007**: Weekly CEO Briefing accurately summarizes all tasks completed
  in the prior 7 days with no tasks missing from the summary.
- **SC-008**: Dry-run mode produces identical log output and vault file
  creation as live mode, differing only in that no real external API calls
  are made.
- **SC-009**: System handles Gmail API errors (auth failure, rate limit,
  network timeout) without crashing, logging clear error messages and
  continuing to poll.
- **SC-010**: Ralph Wiggum loop terminates within 20 iterations for any
  task, logging a warning if task is not complete.
- **SC-011**: End-to-end demo (email arrives → task → plan → approval →
  send → log → briefing) completes successfully, after which the system
  outputs: `SILVER TIER FUNCTIONAL ASSISTANT COMPLETE – READY FOR GOLD UPGRADE`
