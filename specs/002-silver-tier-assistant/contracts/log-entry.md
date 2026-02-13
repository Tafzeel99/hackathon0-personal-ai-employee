# Contract: Log Entry

**Entity**: Log Entry (JSONL)
**Created by**: All scripts (watchers, orchestrator, MCP)
**Location**: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

## File Format

JSONL (JSON Lines) — one JSON object per line, newline-separated.
Files are append-only. One file per calendar day.

**Example filename**: `2026-02-13.json`

## Entry Schema

```json
{
  "timestamp": "2026-02-13T10:30:45+05:00",
  "action": "email_detected",
  "source": "gmail_watcher",
  "task_ref": "Needs_Action/EMAIL_20260213_103045_re-meeting-tomorrow.md",
  "result": "success",
  "details": "Subject: Re: Meeting tomorrow, From: john@example.com"
}
```

### Field Rules

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| timestamp | ISO-8601 | yes | MUST include timezone offset |
| action | string | yes | MUST be from action vocabulary |
| source | string | yes | Script name that generated the entry |
| task_ref | string | no | Relative path to related task file |
| result | enum | yes | `success\|failure\|dry_run\|skipped` |
| details | string | no | Human-readable context (max 500 chars) |

### Action Vocabulary

| Action | Source | Description |
|--------|--------|-------------|
| `file_detected` | `filesystem_watcher` | New file found in watch_inbox |
| `email_detected` | `gmail_watcher` | New unread email found |
| `task_claimed` | `orchestrator` | Task moved to In_Progress |
| `claude_invoked` | `orchestrator` | Claude Code CLI called |
| `plan_created` | `orchestrator` | Plan.md generated |
| `approval_created` | `orchestrator` | Approval request in Pending_Approval |
| `action_approved` | `orchestrator` | File detected in Approved |
| `action_rejected` | `orchestrator` | File detected in Rejected |
| `email_sent` | `email_mcp` | Email sent successfully |
| `email_drafted` | `email_mcp` | Email draft created |
| `email_failed` | `email_mcp` | Email send failed |
| `briefing_generated` | `briefing_generator` | Weekly briefing created |
| `loop_warning` | `orchestrator` | Ralph Wiggum hit iteration cap |
| `error` | any | Generic error |
| `watcher_started` | any watcher | Watcher process started |
| `watcher_poll` | any watcher | Polling cycle completed (no new items) |

### Result Values

| Result | Meaning |
|--------|---------|
| `success` | Action completed as expected |
| `failure` | Action failed (details field explains why) |
| `dry_run` | Action would have executed but dry-run mode is on |
| `skipped` | Action skipped (e.g., no new items to process) |

## Writing Rules

1. Open file in append mode (`'a'`)
2. Write one JSON object per line (no pretty-printing)
3. End each line with `\n`
4. Do NOT write a JSON array wrapper
5. Create the file if it does not exist
6. Use `json.dumps()` with `ensure_ascii=False` for Unicode support

## Reading Rules

1. Open file, read line by line
2. Parse each line as independent JSON object
3. Handle empty lines gracefully (skip them)
4. Handle malformed lines gracefully (log warning, skip)

## Validation Checklist

- [ ] File is named `YYYY-MM-DD.json`
- [ ] Each line is valid JSON
- [ ] All required fields present in each entry
- [ ] `action` is from the vocabulary list
- [ ] `result` is one of the defined values
- [ ] `timestamp` is valid ISO-8601 with timezone
- [ ] No JSON array wrapper (pure JSONL)
