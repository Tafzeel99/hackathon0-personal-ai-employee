<!--
## Sync Impact Report
- **Version change**: 2.0.0 → 3.0.0 (MAJOR: Gold Tier scope expansion —
  adds ERP integration, multi-channel social, weekly audit, resilience
  patterns, documentation artifacts; redefines constraints and success
  criteria; raises Ralph Wiggum cap from 20 to 50)
- **Modified principles**:
  - "Local-First & Privacy-Centric" → "Local-First Extreme" (expanded for
    Odoo self-hosted, multi-API secrets, no cloud sync)
  - "Proactive but Safe" → "Fully Autonomous within Safe Boundaries"
    (reframed: proactive across personal + business domains)
  - "Modularity" → "Modularity & Agent Skills Expansion" (expanded: 4 new
    skills files for Odoo, social, audit, recovery)
  - "Human Accountability" → "Human Accountability & HITL Escalation"
    (expanded: Odoo posts, social replies, payment thresholds, unusual
    patterns)
  - "Spec-Driven & Incremental" → "Spec-Driven & Incremental" (retained,
    updated to reference Gold building on Silver)
  - "Cost & Simplicity" → "Robust Resilience & Simplicity" (reframed:
    adds error recovery, graceful degradation, watchdog; relaxes line limit
    to 200 for complex MCP scripts)
- **Added principles**:
  - Principle VII: Full Auditability (immutable timestamped detailed logs)
  - Principle VIII: Documentation as Artifact (architecture.md +
    lessons_learned.md must be generated)
- **Added sections**:
  - Odoo Integration under Key Standards
  - Social MCPs under Key Standards
  - Weekly Audit under Key Standards
  - Error Handling & Resilience under Key Standards
  - Documentation Artifacts under Key Standards
  - Gold Tier Constraints (replaces Silver Tier Constraints)
  - Silver Heritage section (documents what carries forward)
- **Removed sections**:
  - Silver Tier Constraints (replaced by Gold Tier Constraints)
  - Silver-specific scope boundary table (replaced with Gold-scoped)
- **Templates requiring updates**:
  - `.specify/templates/plan-template.md` — Constitution Check section
    will reference 8 principles + HITL + Odoo + Social gates
    ✅ compatible (gates filled at plan time; no structural change needed)
  - `.specify/templates/spec-template.md` — ✅ compatible (FR-style
    requirements align with Gold success criteria)
  - `.specify/templates/tasks-template.md` — ✅ compatible (phase
    structure maps to Gold build order; Odoo/social tasks fit as user
    stories)
  - `README.md` — ⚠ pending (still references Silver as current tier;
    update after Gold features are implemented)
  - `CLAUDE.md` — ⚠ pending (must be updated for Gold rules after
    constitution is ratified)
- **Deferred items**:
  - README.md update (after Gold implementation)
  - CLAUDE.md update (after constitution ratification)
-->

# Personal AI Employee – Gold Tier Autonomous Employee Constitution

## Core Principles

### I. Local-First Extreme

The Obsidian vault MUST remain the single source of truth for all state,
tasks, plans, approvals, logs, and ERP summaries. External services
(Gmail, Odoo, Facebook, Instagram, X/Twitter) are accessed ONLY through
controlled watchers and MCP servers — never by direct vault mutation from
outside. All secrets MUST live in `.env` (gitignored), never committed to
version control. No cloud sync of secrets or session tokens. Odoo MUST be
self-hosted locally (VM or Docker), not cloud-hosted.

**Rationale**: Privacy-centric design ensures the user owns all data and
all integrations. The vault is portable, auditable, and works offline for
core operations. External systems are always mediated through scripts the
user controls.

### II. Fully Autonomous within Safe Boundaries

The system MUST be proactive across personal and business domains:
detecting events (emails, file drops, Odoo transactions, social
activity), reasoning about them, generating plans, and executing approved
actions. However, any action that is irreversible or affects an external
system (sending email, posting to social media, confirming an Odoo
invoice/payment, replying to social comments) MUST go through the
Human-in-the-Loop (HITL) approval workflow before execution. No
irreversible external action may execute without explicit human approval.

**Rationale**: Full autonomy for detection, reasoning, and drafting — but
a mandatory human gate for anything that cannot be undone. This enables
maximum productivity while preventing unintended consequences.

### III. ERP-Grade Accounting

Odoo Community (19+) MUST serve as the local source of truth for all
financial operations. The system interacts with Odoo via JSON-RPC
external API through a dedicated MCP server. Draft invoices and payments
are created programmatically; confirming/posting MUST require HITL
approval. Vault summaries MUST reflect Odoo state after each transaction.

**Rationale**: ERP integration elevates the AI employee from task manager
to business operations assistant. Using Odoo Community (self-hosted)
maintains the local-first principle while providing real accounting.

### IV. Multi-Channel Social Presence

The system MUST support posting to and fetching activity from at least
three social platforms: Facebook (Graph API), Instagram (Business API),
and X/Twitter (API v2). LinkedIn drafting (from Silver) is retained.
Claude generates post content; MCP servers handle API calls. All posts
MUST go through HITL approval. Social activity summaries MUST be
generated in `/Briefings` or `/Plans`.

**Rationale**: A business employee manages social presence. Multi-channel
coverage ensures the AI employee handles real business communication
across platforms the user actually uses.

### V. Modularity & Agent Skills Expansion

All AI-generated intelligence MUST be encoded as Agent Skills
(`agent_skills/*.md` files), not hardcoded in Python scripts. Scripts
handle ONLY mechanics (polling, moving, logging, API calls). Gold Tier
adds four new Agent Skills: `odoo_skills.md`, `social_summary_skills.md`,
`audit_skills.md`, `recovery_skills.md`. Adding a new capability MUST NOT
require modifying existing scripts — only adding a new skill file and
wiring it into the orchestrator.

**Rationale**: Separating intelligence (Markdown) from mechanics (Python)
makes the system extensible and auditable. New domains (ERP, social,
audit) follow the same pattern established in Bronze/Silver.

### VI. Human Accountability & HITL Escalation

The folder-based HITL workflow MUST gate all external/sensitive actions.
Gold Tier expands HITL to cover: all Odoo confirm/post operations, new
social media replies, payments exceeding a configurable threshold, and
unusual patterns detected in transactions or task queues. Claude (or
orchestrator) creates approval files in `Pending_Approval/`. A human
MUST move to `Approved/` or `Rejected/`. No code path may bypass HITL
for external actions.

**Rationale**: As autonomy scope grows (ERP, multi-platform social),
the HITL surface area grows proportionally. The folder-based pattern
scales without architectural changes.

### VII. Full Auditability

Every decision and action MUST produce an immutable, timestamped,
detailed log entry. Logs MUST include full context: prompt text, response
snippet, MCP call parameters, and outcome. Log files
(`Logs/YYYY-MM-DD.json`) are append-only JSONL. Comprehensive logs MUST
allow full reconstruction of any action sequence. The weekly audit
process MUST verify log integrity.

**Rationale**: An autonomous employee handling finances and public
communications requires a complete audit trail. If something goes wrong,
the logs must tell the full story.

### VIII. Documentation as Artifact

At Gold Tier completion, the system MUST generate two documentation
artifacts in the vault: `architecture.md` (system diagram in
ASCII/Mermaid, component descriptions, data flows) and
`lessons_learned.md` (what worked, what didn't, decisions revisited).
These are deliverables, not optional.

**Rationale**: Documentation is part of the product. A hackathon project
that cannot explain itself is incomplete. These artifacts also serve as
the foundation for Platinum Tier planning.

### IX. Spec-Driven & Incremental

Claude Code MUST generate code and content strictly from this
constitution and referenced spec files. No assumptions from internal
knowledge. Gold Tier MUST build on Silver — the existing vault structure,
watchers, orchestrator, email MCP, and HITL workflow remain intact. New
capabilities (Odoo, social MCPs, audit, resilience) are added one at a
time, tested, and integrated before the next is started.

**Rationale**: Reproducibility and auditability. Incremental delivery
reduces risk and ensures each piece works before complexity increases.

### X. Robust Resilience & Simplicity

The system MUST handle failures gracefully: retry with exponential
backoff for transient API errors, quarantine bad data to a dedicated
folder, restart watchers via a watchdog process, and create alert files
in the vault on critical failures. Despite resilience requirements,
prefer polling and simple scripts over heavy frameworks. Minimize
dependencies. Python scripts SHOULD remain under 200 lines each (relaxed
from 150 for complex MCP integrations). Never introduce a framework when
a simple script suffices.

**Rationale**: Gold Tier integrates with multiple external APIs that can
fail independently. Graceful degradation ensures the system recovers
without human intervention for transient issues, while alerting for
critical ones.

## Key Standards

### Vault Structure

The vault MUST contain these folders and root files (Silver folders
retained; Gold additions marked with `[NEW]`):

```text
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── watch_inbox/              # Drop folder monitored by filesystem watcher
├── Needs_Action/             # Watchers write task files here
├── In_Progress/              # Orchestrator moves claimed tasks here
├── Plans/                    # Claude creates Plan_*.md here
├── Pending_Approval/         # HITL approval requests
├── Approved/                 # Human-approved actions
├── Rejected/                 # Human-rejected actions
├── Done/                     # Completed tasks moved here
├── Inbox/                    # General incoming items
├── Logs/                     # JSONL structured logs (append-only)
├── Briefings/                # CEO Briefings + social summaries
├── Quarantine/               # [NEW] Bad data / failed tasks for review
├── Alerts/                   # [NEW] Critical failure notifications
├── agent_skills/             # Agent Skills (Markdown instructions)
│   ├── planning_skills.md
│   ├── email_skills.md
│   ├── approval_skills.md
│   ├── social_post_skills.md
│   ├── odoo_skills.md         # [NEW] Odoo ERP interaction rules
│   ├── social_summary_skills.md  # [NEW] Multi-platform summary rules
│   ├── audit_skills.md        # [NEW] Weekly audit generation rules
│   └── recovery_skills.md    # [NEW] Error recovery & degradation rules
├── architecture.md            # [NEW] Generated at Gold completion
└── lessons_learned.md         # [NEW] Generated at Gold completion
```

### Agent Skills Pattern

All Claude-generated intelligence MUST live in `agent_skills/*.md` files.
These files describe behavior in Markdown that Claude reads as
instructions. No intelligence is hardcoded in Python scripts; scripts
handle only mechanics.

Gold Tier Agent Skills (extends Silver):
- `planning_skills.md` — Plan.md format and generation rules (from Bronze)
- `email_skills.md` — Email parsing and reply/send drafting (from Silver)
- `approval_skills.md` — HITL routing thresholds (expanded for Gold)
- `social_post_skills.md` — LinkedIn + multi-platform drafting (expanded)
- `odoo_skills.md` — [NEW] Odoo invoice/payment draft rules, field
  mappings, validation, when to flag for HITL
- `social_summary_skills.md` — [NEW] How to fetch and summarise social
  activity across FB/IG/X, what metrics to highlight
- `audit_skills.md` — [NEW] Weekly audit generation: Odoo transaction
  review, revenue calculation, bottleneck analysis, proactive suggestions
- `recovery_skills.md` — [NEW] Error recovery rules: retry policies,
  quarantine criteria, watchdog behavior, alert file format

### Frontmatter Schema

Every file in `Needs_Action/` MUST include this YAML frontmatter (Gold
additions marked with `[NEW]`):

```yaml
---
type: <task_type>           # file_drop | email_inbound | manual |
                            # scheduled | odoo_event | social_activity
created: <ISO-8601>         # e.g., 2026-02-14T10:30:00+05:00
status: pending             # pending | in_progress | done | rejected |
                            # quarantined
priority: normal            # low | normal | high | urgent
source: <trigger>           # e.g., watch_inbox/test.txt, gmail:msg_id,
                            # odoo:invoice_123, social:fb_post_456
action_required: <yes|no>   # Whether external action is needed
hitl_type: <type|null>      # email_send | post_linkedin | post_facebook |
                            # post_instagram | post_x | odoo_confirm |
                            # odoo_payment | null
domain: <domain|null>       # [NEW] email | social | erp | internal | null
---
```

### Plan.md Format

Every file in `Plans/` MUST contain:

- **Objective**: One-sentence description of what the plan achieves
- **Steps**: Checkbox list of concrete actions
- **Status**: pending | in_progress | complete
- **Approval Request**: If the plan requires an external action, it MUST
  include an "Approval Required" section listing action type,
  recipient/target, summary of content
- **LinkedIn/Social Post Draft**: If social posting is needed, full draft
  text in the plan body
- **Odoo Operation**: [NEW] If ERP action needed, include operation type,
  partner, amount, and reference

### HITL Workflow

The Human-in-the-Loop workflow MUST follow this exact sequence:

1. Claude generates a Plan.md that identifies an external action
2. Orchestrator creates an approval file in `Pending_Approval/` with
   frontmatter: `action_type`, `target`, `content_summary`, `plan_ref`
3. Human reviews the file and moves it to:
   - `Approved/` → orchestrator detects and executes via MCP
   - `Rejected/` → orchestrator logs rejection, moves task to `Done/`
     with `status: rejected`
4. After execution, the approval file is moved to `Done/` with result
   logged

HITL escalation triggers (Gold):
- All email sends (retained from Silver)
- All social media posts across all platforms
- All Odoo confirm/post operations (invoices, payments)
- Payments exceeding configurable threshold
- Unusual patterns (spike in transactions, unknown partners)
- New social media replies or comments

No external action may execute without a file appearing in `Approved/`.

### Odoo Integration

Gold Tier MUST include Odoo Community (19+) integration:
- Self-hosted locally via Docker or VM (not Odoo cloud)
- Communication via JSON-RPC external API (`odoorpc` or `xmlrpc.client`)
- Dedicated MCP server: `odoo_mcp.py`
- Supported operations: create draft invoice, create draft payment,
  list invoices/payments, fetch partner info
- HITL required for: confirm invoice, post payment, create new partner
- Vault reflection: after each Odoo operation, update a summary file
  or include in next briefing
- Credentials in `.env`: `ODOO_URL`, `ODOO_DB`, `ODOO_USER`,
  `ODOO_PASSWORD`

### Social MCPs

Gold Tier MUST include MCP servers for at least three social platforms:
- **Facebook**: `social_facebook_mcp.py` — Graph API for page posts +
  fetch recent activity
- **Instagram**: `social_instagram_mcp.py` — Business API for posts +
  fetch recent media/comments
- **X/Twitter**: `social_x_mcp.py` — API v2 for tweets + fetch timeline
  (note: posting may require paid tier; fallback to draft if blocked)
- **LinkedIn**: Retained from Silver (draft-only, manual posting)

Each MCP MUST:
- Accept CLI args (content, media, dry-run)
- Return JSON result to stdout
- Log via `log_utils.log_event`
- Support `--dry-run` mode
- Handle API errors with structured error JSON

### Weekly Audit

Gold Tier upgrades the Monday CEO Briefing to a comprehensive weekly
audit:
- Trigger: Sunday night (or Monday morning) — automated via orchestrator
  schedule check
- Scope: Full review of Odoo transactions + vault `/Done` tasks + social
  activity
- Output: `Briefings/Audit_YYYY-MM-DD.md` with sections:
  1. **Revenue Summary**: Total invoiced, total paid, outstanding, from
     Odoo
  2. **Completed Tasks**: Grouped by domain (email, social, ERP, file)
  3. **Bottleneck Analysis**: Tasks that took longest, approvals that
     waited longest
  4. **Social Activity Summary**: Posts made, engagement metrics
  5. **Proactive Suggestions**: Data-driven recommendations
- Claude reads `audit_skills.md` for formatting and analysis rules

### Error Handling & Resilience

Gold Tier MUST implement robust error handling:
- **Retry with backoff**: Transient API errors (HTTP 429, 500, 503)
  trigger retry with exponential backoff (1s, 2s, 4s, max 60s, max 3
  retries)
- **Quarantine**: Tasks that fail after retries are moved to
  `Quarantine/` with error details in frontmatter
- **Watchdog**: A lightweight watchdog process (`watchdog_monitor.py`)
  checks if watcher/orchestrator processes are alive; restarts if needed
- **Alert files**: Critical failures (auth expired, Odoo down, API
  revoked) create alert files in `Alerts/` with details and suggested
  remediation
- **Graceful degradation**: If one API is down, queue tasks locally and
  resume processing when the API returns; other domains continue
  operating

### Logging

Gold Tier extends structured logging:
- Log files: `Logs/YYYY-MM-DD.json` (append-only JSONL)
- Each entry MUST include: `timestamp` (ISO-8601), `action`, `source`,
  `result`, `task_ref`, `details`
- Gold additions to `details`: MCP call parameters, response snippets,
  Odoo record IDs, social post IDs, retry count
- All watcher detections, orchestrator claims, Claude invocations, HITL
  decisions, MCP executions, retries, quarantines, and alerts MUST be
  logged
- Logs MUST allow full reconstruction of any action sequence

### Ralph Wiggum Loop

For multi-step tasks that require persistence, Claude Code CLI MUST be
invoked in a Ralph Wiggum loop:
- Maximum 50 iterations per task (raised from 20 for complex multi-step
  Gold workflows)
- File-move completion check preferred over promise-based detection
- Each iteration checks for `TASK_COMPLETE` marker in stdout or file
  appearing in `Done/`
- If limit reached without completion, log a hard failure via
  `log_utils`, create alert in `Alerts/`, and move task to `Quarantine/`
- The loop MUST NOT run indefinitely; the iteration cap is non-negotiable

### Orchestrator Pattern

The orchestrator script mediates all vault interactions:
- Claims tasks by moving from `Needs_Action/` to `In_Progress/`
  (claim-by-move prevents duplicate processing; only one active task per
  domain)
- Calls Claude Code with vault context + Agent Skills
- Moves completed tasks to `Done/`
- Polls `Approved/` for HITL-approved actions and dispatches to
  appropriate MCP
- Polls `Quarantine/` and `Alerts/` for operator attention
- Monday schedule check: triggers weekly audit generation
- No direct Claude vault writes — the orchestrator script mediates

### Documentation Artifacts

At Gold Tier completion, MUST generate:
- `AI_Employee_Vault/architecture.md`: System architecture diagram
  (ASCII art or Mermaid), component descriptions, data flow between
  watchers → orchestrator → MCPs → vault, integration points
- `AI_Employee_Vault/lessons_learned.md`: What worked, what didn't,
  decisions that would be made differently, recommendations for Platinum

### Code Standards

- Python files MUST start with:
  ```python
  # Gold Tier – Hackathon 0 – Personal AI Employee
  # Generated following spec.constitution.md
  ```
- Each script SHOULD be < 200 lines (relaxed from 150 for complex MCP
  integrations; prefer splitting into modules if exceeding)
- Polling preferred; watchdog process for monitoring
- Secrets MUST live in `.env` (gitignored), loaded via `os.environ` or
  `python-dotenv`
- Allowed pip installs: `google-api-python-client`, `google-auth-oauthlib`,
  `python-dotenv`, `odoorpc` (or use stdlib `xmlrpc.client`),
  `facebook-sdk` (if simple), `tweepy` or `requests-oauthlib` (for X)
- No heavy frameworks (no Flask, Django, FastAPI for Gold)
- All output files: `.md` and `.json` (logs only)

## Gold Tier Constraints

### Scope Boundary

| In Scope (Gold) | Out of Scope (Platinum) |
|---|---|
| Everything from Silver (retained) | Cloud deployment / hosting |
| Odoo Community self-hosted (Docker/VM) | Odoo cloud / SaaS |
| Odoo MCP: draft invoice/payment + HITL | Full ERP automation (no HITL) |
| Facebook Graph API posting + fetch | WhatsApp Business API |
| Instagram Business API posting + fetch | TikTok / YouTube automation |
| X/Twitter API v2 posting + fetch | Paid ad management |
| LinkedIn drafting (from Silver) | LinkedIn API posting (requires app review) |
| Weekly audit with revenue calc | Real-time financial dashboards |
| Ralph Wiggum loop (50 cap) | Infinite persistence loops |
| Watchdog process restart | Self-healing infrastructure |
| Quarantine + alert files | Auto-remediation of failures |
| architecture.md + lessons_learned.md | Full documentation site |
| Agent Skills expansion (4 new) | Self-modifying AI behavior |
| Cross-domain multi-step tasks | Multi-agent orchestration |

### Trigger Mechanisms

**Filesystem Watcher** (retained from Bronze):
1. Human drops a file into `watch_inbox/`
2. Watcher polls every 15 seconds, detects new file
3. Creates `Needs_Action/TASK_<timestamp>_<filename>.md`
4. Watcher NEVER moves files; only creates task files

**Gmail Watcher** (retained from Silver):
1. Polls Gmail inbox via Google API (OAuth credentials in `.env`)
2. Detects unread emails
3. Creates `Needs_Action/EMAIL_<timestamp>_<subject_slug>.md`
4. Marks email as read after task file creation

**Scheduled Trigger** (expanded for Gold):
1. Orchestrator schedule check: Monday → weekly audit; configurable
   intervals for other recurring tasks
2. Creates `Needs_Action/SCHEDULED_<timestamp>_<task_name>.md`
3. Sunday night trigger for weekly audit generation

**Odoo Event Watcher** `[NEW]`:
1. Polls Odoo for new/changed records (invoices, payments) via JSON-RPC
2. Creates `Needs_Action/ODOO_<timestamp>_<record_type>_<id>.md`
3. Includes Odoo record details in frontmatter

**Social Activity Watcher** `[NEW]`:
1. Polls social platforms for new activity (comments, mentions, DMs)
2. Creates `Needs_Action/SOCIAL_<timestamp>_<platform>_<type>.md`
3. Includes activity details and link to original post

### Success Criteria

- [ ] Odoo running locally (Docker) → MCP drafts invoice/payment →
  HITL approve → posted in Odoo → reflected in vault summary
- [ ] Social channels: Claude generates post → MCP posts (or drafts) →
  fetches recent activity → creates summary in Briefings/
- [ ] Weekly audit runs autonomously: reads Odoo + vault + social →
  produces Audit briefing with revenue, bottlenecks, suggestions
- [ ] Multi-step task (e.g., email trigger → Odoo draft invoice →
  approval → post → social announcement) completes via Ralph loop
- [ ] Graceful degradation: API down → queue task in Quarantine/ →
  alert in Alerts/ → resume on restore
- [ ] End-to-end demo covers cross-domain flow (email/file trigger →
  accounting → social post → audit)
- [ ] Comprehensive logs allow full reconstruction of any action
- [ ] architecture.md + lessons_learned.md generated in vault
- [ ] All HITL escalation triggers enforced (no bypass)
- [ ] Watchdog restarts crashed processes
- [ ] All scripts have Gold header comment and --dry-run support

### Silver Heritage

The following Silver Tier artifacts and patterns carry forward:
- Vault folder structure (extended with Quarantine/, Alerts/)
- `Dashboard.md`, `Company_Handbook.md`, `Business_Goals.md`
- All Silver Agent Skills (planning, email, approval, social_post)
- `filesystem_watcher.py`, `gmail_watcher.py` (retained or extended)
- `orchestrator.py` (extended for Odoo/social dispatch + audit schedule)
- `email_mcp.py` (retained)
- `briefing_generator.py` (extended or replaced by audit generator)
- `log_utils.py` (extended with richer detail fields)
- Frontmatter schema (extended with new types and domain field)
- HITL folder workflow (same pattern, expanded scope)

### Milestone Protocol

After completing any file or milestone, output exactly:

```
GOLD MILESTONE COMPLETE: [short description of completed piece]
```

When the full Gold Tier is demonstrably working end-to-end, output:

```
GOLD TIER AUTONOMOUS EMPLOYEE COMPLETE – READY FOR PLATINUM OR SUBMISSION
```

## Governance

- This constitution is the supreme authority for Gold Tier development.
  It supersedes all other instructions when conflicts arise.
- Amendments require: (1) documentation of what changed, (2) user
  approval, (3) version bump following semver (MAJOR.MINOR.PATCH).
- All code and content MUST be verified against this constitution before
  being marked complete.
- After Gold is complete, this constitution will be amended for Platinum
  Tier scope expansion.
- Use `CLAUDE.md` for runtime development guidance specific to Claude
  Code.
- Silver Tier v2.0.0 constitution is superseded but preserved in git
  history for reference.

**Version**: 3.0.0 | **Ratified**: 2026-02-11 | **Last Amended**: 2026-02-14
