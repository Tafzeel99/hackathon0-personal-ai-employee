# Personal AI Employee — Hackathon 0

Building Autonomous FTEs in 2026, one tier at a time.

## What Is This?

A local-first AI employee that lives inside an Obsidian vault. It watches for tasks you drop into a folder, creates structured task files, and uses Claude Code to turn them into actionable plans — all without any external APIs, cloud services, or dependencies.

**Current Tier: Bronze (Foundation)**

## How It Works

```
You drop a file          Watcher detects it        Claude creates a plan
into watch_inbox/   →    and creates a task    →   in Plans/ following
                         in Needs_Action/          planning_skills.md
```

1. **Drop** a `.txt` or `.md` file into `AI_Employee_Vault/watch_inbox/`
2. **Watcher** (`filesystem_watcher.py`) polls every 15 seconds, detects new files, and creates structured task files with YAML frontmatter in `Needs_Action/`
3. **Process** tasks by running Claude Code with the prompt from `agent_skills/process_tasks_prompt.md`
4. **Plans** appear in `Plans/` with an objective, checkbox steps, and status
5. **Archive** completed tasks to `Done/`

## Quick Start

### Prerequisites

- Python 3.8+
- Claude Code CLI
- Obsidian (optional, for viewing the vault)

### Run It

```bash
# 1. Start the watcher
python filesystem_watcher.py

# 2. Drop a task (in another terminal)
echo "Summarize my weekly tasks" > AI_Employee_Vault/watch_inbox/test-task.txt

# 3. Wait ~15 seconds, then check
ls AI_Employee_Vault/Needs_Action/
# → TASK_test-task_20260211_050500.md

# 4. Process with Claude Code
# Copy the prompt from AI_Employee_Vault/agent_skills/process_tasks_prompt.md
# and run it with Claude Code

# 5. Check the plan
cat AI_Employee_Vault/Plans/Plan_test-task.md
```

## Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Status and recent plans
├── Company_Handbook.md       # Operational rules
├── Business_Goals.md         # Q1 2026 goals
├── agent_skills/
│   ├── planning_skills.md    # Plan format specification
│   └── process_tasks_prompt.md  # Claude Code prompt template
├── watch_inbox/              # Drop files here
├── Needs_Action/             # Watcher creates tasks here
├── Plans/                    # Claude generates plans here
├── Done/                     # Completed tasks archived here
├── In_Progress/              # For future use
├── Inbox/                    # General incoming items
└── Logs/                     # Optional logs
```

## Task File Format

Every task created by the watcher includes YAML frontmatter:

```yaml
---
type: file_drop
created: 2026-02-11T05:05:00+05:00
status: pending
priority: medium
source: watch_inbox/test-task.txt
original_file: test-task.txt
---

Summarize my weekly tasks
```

## Plan File Format

Plans follow the format defined in `planning_skills.md`:

```yaml
---
objective: Summarize the user's weekly tasks into a clear overview
status: complete
---

## Steps
- [ ] Gather all task files from the current week
- [ ] Group tasks by category
- [ ] Write a summary for each category
```

## Bronze Tier Constraints

| Aspect | Allowed | Not Allowed |
| ------ | ------- | ----------- |
| Dependencies | Python stdlib only | No pip installs |
| Execution | Manual prompt + watcher | No auto-orchestration |
| Claude | Manual CLI command | No API calls |
| Network | None | No external calls |
| Intelligence | agent_skills/*.md | No hardcoded logic |

## Tier Roadmap

- **Bronze** — Local vault + file watcher + manual Claude prompts (COMPLETE)
- **Silver** — API watchers, MCP servers, approval workflows
- **Gold** — Scheduling, persistence loop, ERP integration
- **Platinum** — Full autonomous operation with human oversight

## Spec-Driven Development

This project follows the Spec-Kit Plus methodology. All design artifacts live in `specs/001-bronze-tier-foundation/`:

| Artifact | Purpose |
| -------- | ------- |
| `spec.md` | Feature requirements and acceptance criteria |
| `plan.md` | Architecture decisions and build phases |
| `tasks.md` | 17 executable tasks with dependencies |
| `research.md` | Technology decisions and discrepancy resolutions |
| `data-model.md` | Entity schemas and relationships |
| `contracts/` | Task file and plan file format contracts |

All prompt history is recorded in `history/prompts/` for full traceability.

## License

Private — Hackathon 0 project.
