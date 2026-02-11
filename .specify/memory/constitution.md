<!--
## Sync Impact Report
- **Version change**: 0.0.0 → 1.0.0 (MAJOR: initial ratification)
- **Modified principles**: N/A (first version)
- **Added sections**:
  - 5 Core Principles (Local-First, Minimal Viable Foundation, Transparency,
    Human Control, Spec-Driven Development)
  - Key Standards (vault structure, Agent Skills, frontmatter, code rules)
  - Bronze Tier Constraints (scope, triggers, file policy, success criteria)
  - Governance (amendment procedure, versioning, compliance)
- **Removed sections**: All template examples/comments replaced with concrete content
- **Templates requiring updates**:
  - `.specify/templates/plan-template.md` — Constitution Check section will
    reference these 5 principles ✅ compatible (no update needed now,
    gates filled at plan time)
  - `.specify/templates/spec-template.md` — ✅ compatible (functional requirements
    pattern aligns with FR-style success criteria)
  - `.specify/templates/tasks-template.md` — ✅ compatible (phase structure
    maps to Bronze build order)
- **Deferred items**: None
-->

# Personal AI Employee – Bronze Tier Foundation Constitution

## Core Principles

### I. Local-First Architecture

Everything MUST live inside one Obsidian vault folder on the local filesystem.
No cloud services, no remote databases, no network calls.
All state is represented as Markdown files in a defined folder hierarchy.

**Rationale**: Privacy-centric design; the vault is the single source of truth.
Eliminates external dependencies and ensures the system works offline.

### II. Minimal Viable Foundation

Only what is explicitly required for Bronze Tier MUST be built.
No feature creep into Silver/Gold territory (no Gmail, WhatsApp, MCP servers,
Ralph Wiggum loop, scheduling, Odoo, or social media integrations).
Each deliverable MUST be the smallest useful increment.

**Rationale**: Bronze is the foundation layer. Building only what is needed
ensures a solid, testable base before adding complexity in later tiers.

### III. Transparency and Auditability

Every generated file MUST be traceable to a trigger (a file drop, a manual
prompt, or a scheduled event). All task files MUST carry frontmatter metadata
(type, created timestamp, status, priority). All Python scripts MUST include
a header comment identifying the tier and governing spec.

**Rationale**: An autonomous system that modifies files must leave a clear
audit trail. Traceability is non-negotiable for trust and debugging.

### IV. Human Remains in Control

In Bronze Tier, there are NO automatic external actions. The filesystem watcher
detects and creates task files, but ONLY a human (or a human-initiated Claude
prompt) moves tasks through the pipeline. No code may send emails, make
payments, post to social media, or call external APIs.

**Rationale**: Bronze establishes the control pattern before autonomy is
granted. The human-in-the-loop habit must be built into the architecture
from day one.

### V. Spec-Driven Development

Claude Code MUST generate code and content strictly from this constitution
and referenced spec files. No assumptions from internal knowledge. All
methods require verification against project docs. All AI-generated
intelligence MUST be encoded as Agent Skills (`agent_skills/*.md` files),
not hardcoded logic.

**Rationale**: Reproducibility and auditability. Any developer (or future
AI agent) should be able to reproduce the same output given the same specs.

## Key Standards

### Vault Structure

The vault MUST contain exactly these folders and root files:

```text
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── watch_inbox/           # Drop folder monitored by watcher
├── Needs_Action/          # Watcher writes task files here
├── Plans/                 # Claude creates Plan_*.md here
├── Done/                  # Completed tasks moved here
├── Inbox/                 # General incoming items
├── Logs/                  # Watcher and processing logs
└── agent_skills/          # Agent Skills (Markdown instructions)
    └── planning_skills.md
```

Zero deviation from defined folder names is permitted.

### Agent Skills Pattern

All Claude-generated intelligence MUST live in `agent_skills/*.md` files.
These files describe behavior in Markdown that Claude reads as instructions.
No intelligence is hardcoded in Python scripts; scripts handle only
filesystem mechanics (polling, copying, logging).

### Frontmatter Schema

Every file in `Needs_Action/` MUST include this YAML frontmatter:

```yaml
---
type: <task_type>       # e.g., file_drop, manual, scheduled
created: <ISO-8601>     # e.g., 2026-02-11T10:30:00
status: pending         # pending | in_progress | done
priority: normal        # low | normal | high | urgent
source: <trigger>       # e.g., watch_inbox/test-task.txt
---
```

### Plan.md Format

Every file in `Plans/` MUST contain:

- **Objective**: One-sentence description of what the plan achieves
- **Steps**: Checkbox list of concrete actions
- **Status**: pending | in_progress | complete

### Code Standards

- Python files MUST start with:
  ```python
  # Bronze Tier – Hackathon 0 – Personal AI Employee
  # Generated following spec.constitution.md
  ```
- Watcher script MUST be < 150 lines
- Polling preferred over watchdog (no pip installs in Bronze)
- Output files: `.md` only (no JSON, no databases)
- No external dependencies: no pip installs, no APIs, no network calls
- No secrets, no `.env`, no credentials in Bronze

## Bronze Tier Constraints

### Scope Boundary

| In Scope (Bronze) | Out of Scope (Silver/Gold/Platinum) |
|---|---|
| Obsidian vault structure | Gmail/WhatsApp watchers |
| Dashboard.md, Handbook, Goals | MCP servers |
| Filesystem watcher (polling) | Ralph Wiggum loop |
| Needs_Action task creation | Scheduling (cron/Task Scheduler) |
| Manual Claude prompt processing | Human-in-the-loop approval workflow |
| Plan.md generation | Odoo ERP integration |
| Move to Done/ workflow | Social media posting |
| Agent Skills (Markdown) | External API calls |

### Trigger Mechanism

1. Human drops a file into `watch_inbox/`
2. Filesystem watcher (polling, every 15 seconds) detects new file
3. Watcher creates `Needs_Action/TASK_<timestamp>_<filename>.md` with
   frontmatter
4. Watcher NEVER moves files; only creates task files
5. Human runs Claude Code prompt to process `Needs_Action/`
6. Claude reads tasks, creates `Plans/Plan_<name>.md` per planning_skills.md
7. Human (or Claude when prompted) moves completed items to `Done/`

### Success Criteria

- [ ] Vault folder structure exists and opens in Obsidian
- [ ] Dashboard.md, Company_Handbook.md, Business_Goals.md exist with content
- [ ] `agent_skills/planning_skills.md` exists and defines Plan.md format
- [ ] `filesystem_watcher.py` runs and detects new files in `watch_inbox/`
- [ ] Dropping `test-task.txt` in `watch_inbox/` creates
  `Needs_Action/TASK_*.md` with correct frontmatter
- [ ] Claude Code prompt reads `Needs_Action/`, creates `Plans/Plan_*.md`,
  moves original task to `Done/`
- [ ] End-to-end demo works without errors or external dependencies
- [ ] All generated code follows Bronze constraints
- [ ] Zero deviation from defined folder names and frontmatter schema

### Milestone Protocol

After completing any file or milestone, output exactly:

```
BRONZE MILESTONE COMPLETE: [short description of completed piece]
```

When the full Bronze Tier is demonstrably working end-to-end, output:

```
BRONZE TIER FOUNDATION COMPLETE – READY FOR SILVER UPGRADE
```

## Governance

- This constitution is the supreme authority for Bronze Tier development.
  It supersedes all other instructions when conflicts arise.
- Amendments require: (1) documentation of what changed, (2) user approval,
  (3) version bump following semver (MAJOR.MINOR.PATCH).
- All code and content MUST be verified against this constitution before
  being marked complete.
- After Bronze is complete, this constitution will be amended for Silver
  Tier scope expansion.
- Use `CLAUDE.md` for runtime development guidance specific to Claude Code.

**Version**: 1.0.0 | **Ratified**: 2026-02-11 | **Last Amended**: 2026-02-11
