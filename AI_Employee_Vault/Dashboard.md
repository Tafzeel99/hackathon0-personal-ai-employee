# Personal AI Employee Dashboard — Silver Tier

## Status
- Last activity: 2026-02-14
- Bronze Tier: COMPLETE
- Silver Tier: COMPLETE

## Recent Plans
- Plan_test-task.md — Summarize weekly tasks (2026-02-11)

## Pending Approval Queue
Check `Pending_Approval/` for items awaiting human review.
- Email sends, email drafts, and LinkedIn posts require approval.
- Move approved items to `Approved/`, rejected to `Rejected/`.

## Latest Briefing
See `Briefings/` for the most recent Monday CEO Briefing.
- Generated automatically on Mondays or via `python orchestrator.py --generate-briefing`.

## Silver Tier Status
- **Gmail Watcher**: `python gmail_watcher.py` — polls inbox every 120s
- **Orchestrator**: `python orchestrator.py` — claims tasks, invokes Claude, routes HITL
- **Email MCP**: `email_mcp.py` — dispatched by orchestrator after approval
- **Briefing Generator**: `python briefing_generator.py` — weekly CEO summary
- **Filesystem Watcher**: `python filesystem_watcher.py` — watches watch_inbox/ (Bronze)
