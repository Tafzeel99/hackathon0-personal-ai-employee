# Data Model: Silver Tier Functional Assistant

**Branch**: `002-silver-tier-assistant` | **Date**: 2026-02-13

## Entity Overview

All entities are Markdown or JSON files stored in `AI_Employee_Vault/`.
There is no database. State is represented by which folder a file resides
in and the values in its YAML frontmatter.

```text
                    ┌─────────────────┐
                    │  Gmail Watcher   │
                    │  (EMAIL_*.md)    │
                    └────────┬────────┘
                             │ creates
┌─────────────────┐          ▼
│  FS Watcher     │   ┌──────────────┐    move     ┌──────────────┐
│  (TASK_*.md)    │──▶│ Needs_Action │───────────▶│ In_Progress  │
└─────────────────┘   └──────────────┘             └──────┬───────┘
                                                          │ Claude
┌─────────────────┐                                       ▼
│  Scheduler      │                                ┌──────────────┐
│  (SCHEDULED_*)  │──▶ Needs_Action                │   Plans/     │
└─────────────────┘                                └──────┬───────┘
                                                          │
                                              ┌───────────┴───────────┐
                                              │ action_required?      │
                                         no   │                  yes  │
                                              ▼                       ▼
                                       ┌───────────┐         ┌───────────────────┐
                                       │   Done/   │         │ Pending_Approval/ │
                                       └───────────┘         └────────┬──────────┘
                                              ▲                       │ human
                                              │               ┌───────┴───────┐
                                              │               ▼               ▼
                                              │        ┌──────────┐    ┌──────────┐
                                              │        │ Approved │    │ Rejected │
                                              │        └─────┬────┘    └─────┬────┘
                                              │              │ MCP           │ log
                                              │              ▼               │
                                              │        ┌──────────┐          │
                                              └────────│   Done/  │◀─────────┘
                                                       └──────────┘

All transitions logged to Logs/YYYY-MM-DD.json
```

## Entities

### 1. Task File (Email Variant)

**Location**: `Needs_Action/EMAIL_<timestamp>_<subject_slug>.md`
**Created by**: Gmail watcher
**Lifecycle**: `Needs_Action/` → `In_Progress/` → `Done/`

**Frontmatter fields**:

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| type | string | yes | `email_inbound` | Source type |
| created | ISO-8601 | yes | `2026-02-13T10:30:00+05:00` | Creation time |
| status | string | yes | `pending` | Initial status |
| priority | string | yes | `normal` | `low\|normal\|high\|urgent` |
| source | string | yes | `gmail:<message_id>` | Gmail message ID |
| action_required | string | yes | `yes\|no` | Set by Claude after analysis |
| hitl_type | string | yes | `email_send\|post_linkedin\|null` | HITL action category |
| from | string | yes | `sender@example.com` | Email sender |
| subject | string | yes | `Re: Meeting tomorrow` | Email subject |
| message_id | string | yes | `<msg_id>` | Gmail message ID |

**Body**: Email body text (plain text extracted from email).

**Validation rules**:
- `type` MUST be `email_inbound`
- `status` MUST be `pending` on creation
- `action_required` defaults to `no`; updated by Claude
- `hitl_type` defaults to `null`; updated by Claude
- `from` and `subject` MUST never be empty (use `(unknown)` and
  `(no subject)` as fallbacks)

### 2. Task File (Filesystem Variant — Bronze Heritage)

**Location**: `Needs_Action/TASK_<name>_<timestamp>.md`
**Created by**: Filesystem watcher
**Lifecycle**: Same as email variant

**Frontmatter fields**: Same as Bronze (type, created, status, priority,
source, original_file) plus Silver additions (action_required, hitl_type)
added by the orchestrator after Claude analysis.

### 3. Task File (Scheduled Variant)

**Location**: `Needs_Action/SCHEDULED_<timestamp>_<task_name>.md`
**Created by**: Scheduler (orchestrator)
**Lifecycle**: Same as other task files

**Frontmatter fields**: Same base schema with `type: scheduled`.

### 4. Approval Request File

**Location**: `Pending_Approval/APPROVE_<timestamp>_<action_slug>.md`
**Created by**: Orchestrator (after Claude identifies external action)
**Lifecycle**: `Pending_Approval/` → `Approved/` or `Rejected/` → `Done/`

**Frontmatter fields**:

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| action_type | string | yes | `email_send\|email_draft\|post_linkedin` | What to do |
| target | string | yes | `recipient@example.com` or `linkedin` | Action target |
| content_summary | string | yes | `Reply to John about meeting` | Human-readable summary |
| plan_ref | string | yes | `Plans/Plan_meeting-reply.md` | Path to originating plan |
| task_ref | string | yes | `In_Progress/EMAIL_20260213_103000_meeting.md` | Originating task |
| created | ISO-8601 | yes | `2026-02-13T11:00:00+05:00` | Creation time |
| status | string | yes | `pending_approval` | Initial status |

**Body**: Full content preview — the complete email body to be sent, or the
complete LinkedIn post text to be published. The human MUST be able to read
the full content before approving.

**Validation rules**:
- `action_type` MUST be one of the defined values
- `target` MUST be non-empty
- `plan_ref` MUST point to an existing Plan file
- Body MUST contain the complete content (no truncation)

### 5. Plan File (Silver Extension)

**Location**: `Plans/Plan_<name>.md`
**Created by**: Claude Code (via orchestrator)
**Lifecycle**: Created in `Plans/`, moved to `Done/` on completion

**Frontmatter fields**:

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| objective | string | yes | `Reply to John's email about Q1 meeting` | One-sentence goal |
| status | string | yes | `pending\|in_progress\|complete` | Plan status |
| task_ref | string | yes | `In_Progress/EMAIL_*.md` | Source task |
| action_required | string | yes | `yes\|no` | Whether HITL is needed |

**Body sections** (Silver extension):
1. **Steps**: Checkbox list of concrete actions
2. **Approval Required** (conditional): If `action_required: yes`, includes
   action type, target, content summary, and note about HITL file creation
3. **LinkedIn Post Draft** (conditional): If task calls for social posting,
   includes the full draft text (100-300 words, professional tone, CTA)

### 6. Log Entry

**Location**: `Logs/YYYY-MM-DD.json` (JSONL — one JSON object per line)
**Created by**: All scripts (watchers, orchestrator, MCP)
**Lifecycle**: Append-only, never deleted or modified

**Schema**:

```json
{
  "timestamp": "2026-02-13T10:30:00+05:00",
  "action": "email_detected",
  "source": "gmail_watcher",
  "task_ref": "Needs_Action/EMAIL_20260213_103000_meeting.md",
  "result": "success",
  "details": "Subject: Re: Meeting tomorrow, From: john@example.com"
}
```

**Field definitions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| timestamp | ISO-8601 | yes | When the event occurred |
| action | string | yes | Event type (see action vocabulary below) |
| source | string | yes | Which script generated this entry |
| task_ref | string | no | Path to related task file (if applicable) |
| result | string | yes | `success\|failure\|dry_run\|skipped` |
| details | string | no | Human-readable context |

**Action vocabulary**:
- `file_detected` — filesystem watcher found a new file
- `email_detected` — Gmail watcher found a new email
- `task_claimed` — orchestrator moved task to In_Progress
- `claude_invoked` — orchestrator called Claude Code
- `plan_created` — Claude generated a Plan.md
- `approval_created` — orchestrator created approval request
- `action_approved` — human moved file to Approved
- `action_rejected` — human moved file to Rejected
- `email_sent` — MCP sent an email
- `email_drafted` — MCP created a draft
- `email_failed` — MCP email send failed
- `briefing_generated` — briefing generator ran
- `loop_warning` — Ralph Wiggum hit iteration cap
- `error` — generic error

### 7. Briefing File

**Location**: `Briefings/Monday_YYYY-MM-DD.md`
**Created by**: Briefing generator (orchestrator or standalone script)
**Lifecycle**: Created once per week, read-only after creation

**Frontmatter fields**:

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| type | string | yes | `ceo_briefing` | File type |
| period_start | ISO-8601 date | yes | `2026-02-06` | Start of reporting period |
| period_end | ISO-8601 date | yes | `2026-02-13` | End of reporting period |
| generated | ISO-8601 | yes | `2026-02-13T08:00:00+05:00` | Generation time |
| task_count | integer | yes | `12` | Number of completed tasks |

**Body sections**:
1. **Completed Tasks Summary**: Grouped by type (email, file_drop, scheduled)
2. **Pending Items**: Tasks still in `Needs_Action/` or `In_Progress/`
3. **Proactive Suggestion**: One actionable recommendation based on patterns

### 8. Agent Skill File

**Location**: `agent_skills/<skill_name>.md`
**Created by**: Developer (manually)
**Lifecycle**: Read-only at runtime (Claude reads as instructions)

**No frontmatter**. Pure Markdown instructions that Claude reads to
understand how to behave for a specific capability.

**Silver Tier skills**:
- `planning_skills.md` — Plan format rules (Bronze heritage)
- `process_tasks_prompt.md` — Task processing prompt (Bronze heritage)
- `email_skills.md` — Email analysis, reply drafting, when to suggest send
- `approval_skills.md` — HITL threshold rules, approval file format
- `social_post_skills.md` — LinkedIn post tone, length, CTA patterns

## State Transitions

### Task Lifecycle

```
pending (Needs_Action/) → in_progress (In_Progress/) → done (Done/)
                                                     → rejected (Done/, via Rejected/)
```

### Approval Lifecycle

```
pending_approval (Pending_Approval/) → approved (Approved/) → executed (Done/)
                                     → rejected (Rejected/) → logged (Done/)
```
