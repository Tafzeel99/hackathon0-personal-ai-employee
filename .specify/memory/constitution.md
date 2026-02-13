<!--
## Sync Impact Report
- **Version change**: 1.0.0 → 2.0.0 (MAJOR: Silver Tier scope expansion)
- **Modified principles**:
  - "Local-First Architecture" → "Local-First & Privacy-Centric" (expanded)
  - "Minimal Viable Foundation" → "Modularity" (reframed)
  - "Transparency and Auditability" → "Transparency & Auditability" (retained,
    minor wording update for JSON logs)
  - "Human Remains in Control" → "Human Accountability" (reframed for HITL)
  - "Spec-Driven Development" → "Spec-Driven & Incremental" (expanded)
- **Added sections**:
  - Principle VI: Cost & Simplicity (new)
  - HITL Workflow section under Key Standards
  - MCP Integration section under Key Standards
  - Scheduling section under Key Standards
  - Ralph Wiggum Loop section under Key Standards
  - Silver Tier Constraints (replaces Bronze Tier Constraints)
  - Bronze Heritage section (documents what carries forward)
- **Removed sections**:
  - Bronze Tier Constraints (replaced by Silver Tier Constraints)
  - Scope Boundary table (replaced with Silver-scoped version)
- **Templates requiring updates**:
  - `.specify/templates/plan-template.md` — Constitution Check section will
    reference 6 principles + HITL approval gate ✅ compatible (gates filled
    at plan time; no structural change needed)
  - `.specify/templates/spec-template.md` — ✅ compatible (FR-style
    requirements align with Silver success criteria)
  - `.specify/templates/tasks-template.md` — ✅ compatible (phase structure
    maps to Silver build order; HITL tasks fit as user stories)
  - `README.md` — ⚠ pending (still references Bronze as current tier;
    update after Silver features are implemented)
  - `CLAUDE.md` — ⚠ pending (still references Bronze rules; update after
    constitution is ratified for Silver)
- **Deferred items**:
  - README.md update (update when Silver implementation begins)
  - CLAUDE.md update (update after constitution ratification)
-->

# Personal AI Employee – Silver Tier Functional Assistant Constitution

## Core Principles

### I. Local-First & Privacy-Centric

The Obsidian vault MUST remain the single source of truth for all state,
tasks, plans, approvals, and logs. External services (Gmail, LinkedIn) are
accessed ONLY through controlled watchers and MCP servers — never by direct
vault mutation from outside. All secrets MUST live in `.env` (gitignored),
never committed to version control.

**Rationale**: Privacy-centric design ensures the user owns all data. The
vault is portable, auditable, and works offline for all core operations.
External integrations read from or write to the vault through mediated
scripts, never directly.

### II. Proactive but Safe

Watchers MUST detect events (file drops, new emails) and create structured
task files automatically. Claude MUST reason about tasks and generate plans.
However, any action that affects an external system (sending email, posting
to LinkedIn, calling an API) MUST go through the Human-in-the-Loop (HITL)
approval workflow before execution. No external action may execute without
an explicit human approval step.

**Rationale**: Autonomy without accountability is dangerous. The system
detects and proposes proactively, but a human gate prevents unintended
external consequences. This builds trust incrementally.

### III. Modularity

All AI-generated intelligence MUST be encoded as Agent Skills
(`agent_skills/*.md` files), not hardcoded in Python scripts. Scripts handle
ONLY filesystem mechanics (polling, copying, moving, logging, API calls).
Each capability (planning, email handling, approval routing, social posting)
MUST be a separate Agent Skill file. Adding a new capability MUST NOT
require modifying existing scripts — only adding a new skill file and
wiring it into the orchestrator.

**Rationale**: Separating intelligence (Markdown) from mechanics (Python)
makes the system extensible and auditable. Any developer or future AI agent
can understand, modify, or replace a capability by editing a single file.

### IV. Human Accountability

Silver Tier introduces folder-based HITL for all external/sensitive actions.
Claude MUST create approval request files in `Pending_Approval/`. A human
MUST move the file to `Approved/` (to authorize) or `Rejected/` (to deny).
The orchestrator MUST poll these folders and execute only approved actions.
Rejected actions MUST be logged and the task moved to `Done/` with a
`status: rejected` frontmatter field. No code path may bypass HITL for
external actions.

**Rationale**: Human accountability is a non-negotiable architectural
pattern. Even as autonomy increases in Gold/Platinum tiers, the HITL folder
pattern remains — only the scope of auto-approved actions changes.

### V. Spec-Driven & Incremental

Claude Code MUST generate code and content strictly from this constitution
and referenced spec files. No assumptions from internal knowledge. All
methods require verification against project docs. Silver Tier MUST build
on Bronze — the existing vault structure, watcher, and plan generation
remain intact. New capabilities are added one at a time, tested, and
integrated before the next is started.

**Rationale**: Reproducibility and auditability. Incremental delivery
reduces risk and ensures each piece works before complexity increases.

### VI. Cost & Simplicity

Prefer polling and simple scripts over heavy frameworks. Minimize API usage
and external calls. Use the smallest viable dependency set. Python scripts
MUST remain under 150 lines each. Prefer stdlib where possible; allow
minimal pip installs only when stdlib cannot achieve the goal (e.g.,
`google-api-python-client` for Gmail). Never introduce a framework when a
simple script suffices.

**Rationale**: This is a hackathon project. Complexity is the enemy of
shipping. Every dependency is a maintenance burden and a potential failure
point.

## Key Standards

### Vault Structure

The vault MUST contain these folders and root files (Bronze folders
retained; Silver additions marked with `[NEW]`):

```text
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── watch_inbox/              # Drop folder monitored by filesystem watcher
├── Needs_Action/             # Watchers write task files here
├── In_Progress/              # Orchestrator moves claimed tasks here
├── Plans/                    # Claude creates Plan_*.md here
├── Pending_Approval/         # [NEW] HITL approval requests
├── Approved/                 # [NEW] Human-approved actions
├── Rejected/                 # [NEW] Human-rejected actions
├── Done/                     # Completed tasks moved here
├── Inbox/                    # General incoming items
├── Logs/                     # JSON-format logs (upgraded from text)
└── agent_skills/             # Agent Skills (Markdown instructions)
    ├── planning_skills.md
    ├── email_skills.md       # [NEW] Email handling intelligence
    ├── approval_skills.md    # [NEW] HITL routing intelligence
    └── social_post_skills.md # [NEW] LinkedIn post drafting intelligence
```

### Agent Skills Pattern

All Claude-generated intelligence MUST live in `agent_skills/*.md` files.
These files describe behavior in Markdown that Claude reads as instructions.
No intelligence is hardcoded in Python scripts; scripts handle only
filesystem mechanics (polling, copying, moving, logging, API calls).

Silver Tier Agent Skills:
- `planning_skills.md` — Plan.md format and generation rules (from Bronze)
- `email_skills.md` — How to parse emails, create task files from them,
  and draft reply/send actions
- `approval_skills.md` — When HITL is needed, how to create approval
  request files, what metadata to include
- `social_post_skills.md` — LinkedIn post drafting rules, tone, format

### Frontmatter Schema

Every file in `Needs_Action/` MUST include this YAML frontmatter (Silver
additions marked with `[NEW]`):

```yaml
---
type: <task_type>           # file_drop | email_inbound | manual | scheduled
created: <ISO-8601>         # e.g., 2026-02-13T10:30:00
status: pending             # pending | in_progress | done | rejected
priority: normal            # low | normal | high | urgent
source: <trigger>           # e.g., watch_inbox/test.txt, gmail:msg_id
action_required: <yes|no>   # [NEW] Whether external action is needed
hitl_type: <type|null>      # [NEW] email_send | post_linkedin | null
---
```

### Plan.md Format

Every file in `Plans/` MUST contain:

- **Objective**: One-sentence description of what the plan achieves
- **Steps**: Checkbox list of concrete actions
- **Status**: pending | in_progress | complete
- **Approval Request** `[NEW]`: If the plan requires an external action
  (email send, LinkedIn post), it MUST include an "Approval Required"
  section listing: action type, recipient/target, summary of content,
  and a note that an approval file will be created in `Pending_Approval/`

### HITL Workflow

The Human-in-the-Loop workflow MUST follow this exact sequence:

1. Claude generates a Plan.md that identifies an external action
2. Claude (or orchestrator) creates an approval file in `Pending_Approval/`
   with frontmatter: `action_type`, `target`, `content_summary`, `plan_ref`
3. Human reviews the file and moves it to:
   - `Approved/` → orchestrator detects and executes via MCP or API
   - `Rejected/` → orchestrator logs rejection and moves task to `Done/`
     with `status: rejected`
4. After execution, the approval file is moved to `Done/` with result logged

No external action may execute without a file appearing in `Approved/`.

### MCP Integration

Silver Tier MUST include at least one MCP server:
- **email-mcp**: Handles Gmail send/draft operations via Google API OAuth
- MCP servers receive instructions from the orchestrator ONLY after HITL
  approval
- MCP servers MUST NOT directly read or write vault files — the
  orchestrator mediates all vault mutations

### Logging

Silver Tier upgrades logging from text to structured JSON:
- Log files: `Logs/YYYY-MM-DD.json`
- Each entry MUST include: `action`, `timestamp` (ISO-8601), `result`,
  `source`, `task_ref`
- Logs are append-only (one JSON object per line, JSONL format)
- All watcher detections, orchestrator claims, Claude invocations, HITL
  decisions, and MCP executions MUST be logged

### Scheduling

Silver Tier introduces basic scheduling:
- Simple cron job or Python loop for recurring tasks
- Primary use case: Weekly CEO Briefing generation
  - Runs on schedule (e.g., every Friday)
  - Reads all files in `Done/` from the past week
  - Generates `Plans/Briefing_YYYY-MM-DD.md` with summary
- No complex scheduling framework; a simple polling loop or system cron
  suffices

### Ralph Wiggum Loop

For multi-step tasks that require persistence, Claude Code CLI MUST be
invoked in a Ralph Wiggum loop:
- Maximum 20–30 iterations per task
- Each iteration checks for `TASK_COMPLETE` marker or file in `Done/`
- If limit reached without completion, log a warning and stop
- The loop MUST NOT run indefinitely; the iteration cap is non-negotiable

### Orchestrator Pattern

The orchestrator script mediates all vault interactions:
- Claims tasks by moving from `Needs_Action/` to `In_Progress/`
  (file claim-by-move prevents duplicate processing)
- Calls Claude Code with vault context + Agent Skills
- Moves completed tasks to `Done/`
- Polls `Approved/` for HITL-approved actions and dispatches to MCP
- No direct Claude vault writes — the orchestrator script mediates

### Code Standards

- Python files MUST start with:
  ```python
  # Silver Tier – Hackathon 0 – Personal AI Employee
  # Generated following spec.constitution.md
  ```
- Each script MUST be < 150 lines
- Polling preferred; watchdog allowed only if already installed
- Secrets MUST live in `.env` (gitignored), loaded via `os.environ` or
  `python-dotenv`
- Minimal pip installs allowed: `google-api-python-client`,
  `oauth2client` (or `google-auth`), `python-dotenv`
- No heavy frameworks (no Flask, Django, FastAPI for Silver)
- All output files: `.md` and `.json` (logs only)

## Silver Tier Constraints

### Scope Boundary

| In Scope (Silver) | Out of Scope (Gold/Platinum) |
|---|---|
| Filesystem watcher (from Bronze) | Odoo ERP integration |
| Gmail watcher (Google API OAuth) | WhatsApp Playwright automation |
| Email MCP server (send/draft) | Full social media management |
| Basic LinkedIn post drafting | Cloud deployment |
| Folder-based HITL workflow | Auto-approved action categories |
| JSON structured logging | Database storage |
| Weekly CEO Briefing (scheduled) | Complex scheduling framework |
| Ralph Wiggum loop (capped) | Infinite persistence loops |
| Orchestrator script | Multi-agent orchestration |
| Agent Skills expansion | Self-modifying AI behavior |

### Trigger Mechanisms

**Filesystem Watcher** (retained from Bronze):
1. Human drops a file into `watch_inbox/`
2. Watcher polls every 15 seconds, detects new file
3. Creates `Needs_Action/TASK_<timestamp>_<filename>.md` with frontmatter
4. Watcher NEVER moves files; only creates task files

**Gmail Watcher** `[NEW]`:
1. Polls Gmail inbox via Google API (OAuth credentials in `.env`)
2. Detects unread emails matching configured criteria
3. Creates `Needs_Action/EMAIL_<timestamp>_<subject_slug>.md` with
   frontmatter including `type: email_inbound`, sender, subject, body
4. Marks email as read after task file creation
5. MUST NOT send replies automatically — only create task files

**Scheduled Trigger** `[NEW]`:
1. Cron or Python loop fires on schedule
2. Creates `Needs_Action/SCHEDULED_<timestamp>_<task_name>.md`
3. Orchestrator processes like any other task

### Success Criteria

- [ ] Two watchers running: filesystem watcher detects file drops;
  Gmail watcher detects unread emails — both create task files in
  `Needs_Action/`
- [ ] Orchestrator script claims tasks (move to `In_Progress/`), calls
  Claude Code with vault context + Agent Skills
- [ ] Claude generates Plan.md; if HITL needed, creates approval file
  in `Pending_Approval/`
- [ ] Human moves approval file to `Approved/` → orchestrator detects →
  calls MCP to send email or draft LinkedIn post
- [ ] Basic LinkedIn post generation: Claude drafts post content in
  Plan.md; human approves; MCP or manual posts
- [ ] Weekly CEO Briefing: scheduled task generates
  `Plans/Briefing_YYYY-MM-DD.md` summarizing `Done/` tasks
- [ ] End-to-end demo works: email arrives → task → plan → approval →
  send → log → move to `Done/`
- [ ] All code follows Bronze constraints + Silver additions
- [ ] Zero external actions execute without HITL approval path
- [ ] JSON logging captures all system events
- [ ] Ralph Wiggum loop runs within iteration cap

### Bronze Heritage

The following Bronze Tier artifacts and patterns carry forward unchanged:
- Vault folder structure (extended, not replaced)
- `Dashboard.md`, `Company_Handbook.md`, `Business_Goals.md`
- `agent_skills/planning_skills.md`
- `filesystem_watcher.py` (retained as-is or minimally extended)
- Frontmatter schema (extended with new fields, not replaced)
- Plan.md format (extended with approval section, not replaced)

### Milestone Protocol

After completing any file or milestone, output exactly:

```
SILVER MILESTONE COMPLETE: [short description of completed piece]
```

When the full Silver Tier is demonstrably working end-to-end, output:

```
SILVER TIER FUNCTIONAL ASSISTANT COMPLETE – READY FOR GOLD UPGRADE
```

## Governance

- This constitution is the supreme authority for Silver Tier development.
  It supersedes all other instructions when conflicts arise.
- Amendments require: (1) documentation of what changed, (2) user approval,
  (3) version bump following semver (MAJOR.MINOR.PATCH).
- All code and content MUST be verified against this constitution before
  being marked complete.
- After Silver is complete, this constitution will be amended for Gold
  Tier scope expansion.
- Use `CLAUDE.md` for runtime development guidance specific to Claude Code.
- Bronze Tier v1.0.0 constitution is superseded but preserved in git
  history for reference.

**Version**: 2.0.0 | **Ratified**: 2026-02-11 | **Last Amended**: 2026-02-13
