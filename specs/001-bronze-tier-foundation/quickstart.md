# Quickstart: Bronze Tier Foundation

**Feature**: 001-bronze-tier-foundation
**Date**: 2026-02-11

## Prerequisites

- Python 3.8+ installed
- Claude Code CLI available
- Obsidian installed (optional — any Markdown viewer works)

## Setup

### Step 1: Create the Vault

The vault structure and core files are created as part of implementation. After running the setup, verify:

```bash
ls -R AI_Employee_Vault/
```

Expected output:
```
AI_Employee_Vault/:
Business_Goals.md  Company_Handbook.md  Dashboard.md  Done/  In_Progress/
Inbox/  Logs/  Needs_Action/  Plans/  agent_skills/  watch_inbox/

AI_Employee_Vault/agent_skills:
planning_skills.md
```

### Step 2: Open in Obsidian (optional)

Open `AI_Employee_Vault/` as an Obsidian vault to browse Dashboard, Handbook, and Goals files.

## Running the File Watcher

### Start the watcher

```bash
python filesystem_watcher.py
```

Expected console output:
```
[2026-02-11 04:07:00] Watcher started. Monitoring AI_Employee_Vault/watch_inbox/
[2026-02-11 04:07:00] Polling every 15 seconds for .txt and .md files...
```

### Drop a test file

While the watcher is running, create a test file:

```bash
echo "Summarize my weekly tasks" > AI_Employee_Vault/watch_inbox/test-task.txt
```

Within 15 seconds, the watcher will output:
```
[2026-02-11 04:07:15] New file detected: test-task.txt
[2026-02-11 04:07:15] Created task: Needs_Action/TASK_test-task_20260211_040715.md
```

### Verify the task file

```bash
cat AI_Employee_Vault/Needs_Action/TASK_test-task_*.md
```

Expected:
```yaml
---
type: file_drop
created: 2026-02-11T04:07:15+05:00
status: pending
priority: medium
source: watch_inbox/test-task.txt
original_file: test-task.txt
---

Summarize my weekly tasks
```

## Processing Tasks with Claude

### Run the processing prompt

Ask Claude Code to process pending tasks:

```
Read all files in AI_Employee_Vault/Needs_Action/ that have status: pending.
For each one, read AI_Employee_Vault/agent_skills/planning_skills.md for the output format.
Create a Plan file in AI_Employee_Vault/Plans/ following the planning skill format.
```

### Verify the plan

```bash
cat AI_Employee_Vault/Plans/Plan_test-task.md
```

Expected format:
```markdown
---
objective: Summarize the user's weekly tasks into a clear overview
status: complete
---

## Steps
- [ ] Gather all task files from the current week
- [ ] Group tasks by category
- [ ] Write a summary for each category
- [ ] Highlight overdue items
```

## Completing the Flow

### Move task to Done/

```bash
mv AI_Employee_Vault/Needs_Action/TASK_test-task_*.md AI_Employee_Vault/Done/
```

### Stop the watcher

Press `Ctrl+C` in the watcher terminal.

## End-to-End Timing

The full flow — file drop to plan file — should complete in under 2 minutes:
- Watcher detection: ~15 seconds (one poll cycle)
- Claude processing: ~30 seconds (manual prompt)
- Total: < 1 minute typical

## Troubleshooting

| Issue | Solution |
| ----- | -------- |
| Watcher won't start | Verify `AI_Employee_Vault/watch_inbox/` exists |
| No task file created | Check file extension is `.txt` or `.md` |
| Duplicate tasks on restart | Expected — watcher uses in-memory tracking; restart re-processes existing files |
| Python not found | Ensure Python 3.8+ is in PATH |
