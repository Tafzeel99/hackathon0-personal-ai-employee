# Quickstart: Silver Tier Functional Assistant

**Branch**: `002-silver-tier-assistant` | **Date**: 2026-02-13

## Prerequisites

- Python 3.8+
- Claude Code CLI installed and authenticated
- Google Cloud project with Gmail API enabled
- Obsidian (optional, for viewing the vault)

## 1. Install Dependencies

```bash
pip install google-api-python-client google-auth-oauthlib python-dotenv
```

## 2. Configure Gmail OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use existing)
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download `credentials.json` to the project root

```bash
# Copy the template and fill in your values
cp .env.example .env
```

Edit `.env`:

```env
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_POLL_INTERVAL=120
DRY_RUN=true
```

## 3. First-Time Gmail Authentication

```bash
# Run the Gmail watcher — it will open a browser for OAuth consent
python gmail_watcher.py --auth-only
```

This creates `token.json` which is reused for subsequent runs.

## 4. Create Silver Vault Folders

If not already created, add the Silver-specific folders:

```bash
mkdir -p AI_Employee_Vault/Pending_Approval
mkdir -p AI_Employee_Vault/Approved
mkdir -p AI_Employee_Vault/Rejected
mkdir -p AI_Employee_Vault/Briefings
```

## 5. Start the Watchers

```bash
# Terminal 1: Filesystem watcher (from Bronze)
python filesystem_watcher.py

# Terminal 2: Gmail watcher
python gmail_watcher.py
```

## 6. Start the Orchestrator

```bash
# Terminal 3: Orchestrator (processes tasks + handles HITL)
python orchestrator.py
```

The orchestrator will:
- Poll `Needs_Action/` for new task files
- Claim tasks by moving to `In_Progress/`
- Invoke Claude Code for plan generation
- Create approval files in `Pending_Approval/` when external actions needed
- Poll `Approved/` and `Rejected/` for HITL decisions
- Execute approved actions via MCP

## 7. Test the Full Flow

### Test A: File Drop (Bronze path still works)

```bash
echo "Summarize Q1 goals" > AI_Employee_Vault/watch_inbox/test-q1.txt
# Wait 15 seconds
ls AI_Employee_Vault/Needs_Action/
# → TASK_test-q1_*.md appears
# Wait for orchestrator to process
ls AI_Employee_Vault/Plans/
# → Plan_test-q1.md appears
```

### Test B: Email Flow (Silver path)

```bash
# Send a test email to the monitored Gmail account
# Wait 120 seconds for gmail_watcher to detect it
ls AI_Employee_Vault/Needs_Action/
# → EMAIL_*_test-subject.md appears
# Wait for orchestrator
ls AI_Employee_Vault/Pending_Approval/
# → APPROVE_*_email-reply-*.md appears (if Claude decides reply needed)

# Review the approval file, then approve:
mv AI_Employee_Vault/Pending_Approval/APPROVE_*.md AI_Employee_Vault/Approved/

# Check execution:
ls AI_Employee_Vault/Done/
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### Test C: LinkedIn Draft

```bash
echo "Draft a LinkedIn post about our AI automation hackathon" \
  > AI_Employee_Vault/watch_inbox/linkedin-post.txt
# Wait for processing
# Check Plans/ for LinkedIn draft section
# Check Pending_Approval/ for the post approval file
```

### Test D: CEO Briefing

```bash
python orchestrator.py --generate-briefing
# or
python briefing_generator.py
ls AI_Employee_Vault/Briefings/
# → Monday_2026-02-13.md appears
```

## 8. Dry-Run Mode

All scripts support `--dry-run` mode. Set `DRY_RUN=true` in `.env` or pass
the flag:

```bash
python gmail_watcher.py --dry-run
python orchestrator.py --dry-run
python email_mcp.py --dry-run --to test@example.com --subject "Test"
```

In dry-run mode:
- No emails are sent
- No Gmail messages are marked as read
- All file operations and logging still occur
- Log entries show `"result": "dry_run"`

## Verification

After running all tests, confirm:

- [ ] `AI_Employee_Vault/Needs_Action/` — processed files moved out
- [ ] `AI_Employee_Vault/In_Progress/` — empty (no stuck tasks)
- [ ] `AI_Employee_Vault/Plans/` — plan files created
- [ ] `AI_Employee_Vault/Pending_Approval/` — empty after approvals
- [ ] `AI_Employee_Vault/Done/` — completed tasks archived
- [ ] `AI_Employee_Vault/Logs/YYYY-MM-DD.json` — log entries present
- [ ] `AI_Employee_Vault/Briefings/` — briefing file present
