# Personal AI Employee — Hackathon 0

Building Autonomous FTEs in 2026, one tier at a time.

## What Is This?

A local-first AI employee that lives inside an Obsidian vault. It watches Gmail and a local folder for incoming tasks, creates structured plans using Claude Code, routes external actions through human-in-the-loop (HITL) approval, sends emails via Gmail API, drafts LinkedIn posts, and generates weekly CEO Briefings — all running on your own machine.

**Current Tier: Silver (Functional Assistant)**

## How It Works

```
Gmail inbox           Orchestrator claims task     Claude creates a plan
  or file drop   →    moves to In_Progress/    →   with steps + HITL flags
                                                         │
                                          ┌──────────────┴──────────────┐
                                          │                             │
                                    action_required?              No action needed
                                          │                             │
                                    Pending_Approval/             Move to Done/
                                          │
                                   Human approves/rejects
                                          │
                                 ┌────────┴────────┐
                                 │                  │
                            Approved/          Rejected/
                            Email MCP          Log + Done/
                            or log post
```

1. **Gmail Watcher** polls your inbox every 120s, creates `EMAIL_*.md` task files in `Needs_Action/`
2. **Filesystem Watcher** polls `watch_inbox/` every 15s for file drops, creates `TASK_*.md` files
3. **Orchestrator** claims tasks (move to `In_Progress/`), invokes Claude Code, generates plans
4. **HITL Approval**: Plans requiring external action create files in `Pending_Approval/` — you move them to `Approved/` or `Rejected/`
5. **Email MCP** sends or drafts Gmail messages after approval
6. **LinkedIn posts** are logged as ready for manual posting after approval
7. **CEO Briefing** generated weekly (Mondays) summarising completed tasks, pending items, and a proactive suggestion

## Quick Start

### Prerequisites

- Python 3.8+
- Claude Code CLI
- Gmail API credentials (`credentials.json` from Google Cloud Console)
- Obsidian (optional, for viewing the vault)

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your Gmail credentials path

# 3. Authenticate Gmail (first time only)
python gmail_watcher.py --auth-only
```

### Run It

```bash
# Terminal 1: Start the filesystem watcher (Bronze)
python filesystem_watcher.py

# Terminal 2: Start the Gmail watcher
python gmail_watcher.py

# Terminal 3: Start the orchestrator
python orchestrator.py
```

### Dry-Run Mode

All scripts support `--dry-run` to test without side effects:

```bash
python orchestrator.py --dry-run --once    # Process one task cycle, no Gmail/Claude calls
python gmail_watcher.py --dry-run          # Detect emails without marking as read
python email_mcp.py --to test@example.com --subject "Test" --body "Hello" --dry-run
python briefing_generator.py --dry-run     # Preview briefing without writing file
```

### Demo Flow

```bash
# Drop a task
echo "Summarize my weekly tasks" > AI_Employee_Vault/watch_inbox/test-task.txt

# Wait ~15s for filesystem watcher, then run orchestrator
python orchestrator.py --dry-run --once

# Check results
ls AI_Employee_Vault/Done/          # Completed task + plan
ls AI_Employee_Vault/Logs/          # JSONL structured logs

# Generate a CEO Briefing
python orchestrator.py --generate-briefing
cat AI_Employee_Vault/Briefings/Monday_*.md
```

## Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md                # Status, approval queue, briefing link
├── Company_Handbook.md         # Operational rules + HITL policy
├── Business_Goals.md           # Q1 2026 goals + weekly review cadence
├── agent_skills/
│   ├── planning_skills.md      # Plan format + Silver extensions
│   ├── process_tasks_prompt.md # Claude Code prompt template
│   ├── email_skills.md         # Email handling rules
│   ├── approval_skills.md      # HITL threshold rules
│   └── social_post_skills.md   # LinkedIn drafting guidelines
├── watch_inbox/                # Drop files here (filesystem watcher)
├── Needs_Action/               # Watchers create tasks here
├── In_Progress/                # Orchestrator claims tasks here
├── Plans/                      # Claude generates plans here
├── Pending_Approval/           # HITL: awaiting human review
├── Approved/                   # Human-approved actions
├── Rejected/                   # Human-rejected actions
├── Done/                       # Completed tasks archived here
├── Briefings/                  # Weekly CEO Briefings
├── Inbox/                      # General incoming items
└── Logs/                       # JSONL structured event logs
```

## Scripts

| Script | Lines | Purpose |
|--------|-------|---------|
| `filesystem_watcher.py` | ~80 | Polls `watch_inbox/` for file drops, creates TASK_*.md |
| `gmail_watcher.py` | 150 | Polls Gmail inbox, creates EMAIL_*.md, marks as read |
| `orchestrator.py` | 150 | Claims tasks, invokes Claude, HITL routing, approval dispatch |
| `email_mcp.py` | 109 | Sends/drafts Gmail after HITL approval |
| `briefing_generator.py` | 112 | Weekly CEO Briefing from Done/ tasks |
| `log_utils.py` | 45 | Shared JSONL logging utility |

All scripts stay under 150 lines per constitution. All support `--dry-run`.

## HITL Approval Workflow

The system **never** sends emails or posts to LinkedIn without human approval:

1. Orchestrator detects `action_required: yes` in Claude's plan
2. Creates an approval file in `Pending_Approval/` with full content preview
3. **You** review the file and move it to `Approved/` or `Rejected/`
4. Orchestrator detects the move and dispatches (email MCP) or logs (LinkedIn)
5. Everything moves to `Done/` with structured log entries

## Silver Tier Constraints

| Aspect | Allowed | Not Allowed |
|--------|---------|-------------|
| Dependencies | stdlib + 3 pip packages | Heavy frameworks |
| Execution | Orchestrator + watchers | No auto-orchestration without HITL |
| Claude | CLI via subprocess | No direct API calls |
| External | Gmail API (OAuth), LinkedIn draft | No auto-posting, no WhatsApp |
| Intelligence | agent_skills/*.md | No hardcoded logic |
| Scripts | < 150 lines each | No monolithic files |
| Secrets | `.env` (gitignored) | Never committed |

## Tier Roadmap

- **Bronze** — Local vault + file watcher + manual Claude prompts (COMPLETE)
- **Silver** — Gmail watcher, email MCP, HITL approval, LinkedIn drafts, CEO Briefing (COMPLETE)
- **Gold** — Scheduling, persistence loop, ERP integration
- **Platinum** — Full autonomous operation with human oversight

## Spec-Driven Development

This project follows the Spec-Kit Plus methodology. Design artifacts live in `specs/`:

| Artifact | Purpose |
|----------|---------|
| `spec.md` | Feature requirements and acceptance criteria |
| `plan.md` | Architecture decisions and build phases |
| `tasks.md` | Executable tasks with dependencies |
| `research.md` | Technology decisions |
| `data-model.md` | Entity schemas and relationships |
| `contracts/` | File format contracts (email, approval, briefing, log) |

All prompt history is recorded in `history/prompts/` for full traceability.

## License

Private — Hackathon 0 project.
