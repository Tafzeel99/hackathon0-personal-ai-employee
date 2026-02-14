# Personal AI Employee Dashboard — Gold Tier

## Status
- Last activity: 2026-02-15
- Bronze Tier: COMPLETE
- Silver Tier: COMPLETE
- Gold Tier: COMPLETE

## System Health
- **Watchdog**: `python watchdog_monitor.py` — monitors all processes
- **Orchestrator**: Running / check `orchestrator.pid`
- **Gmail Watcher**: Running / check `gmail_watcher.pid`
- **Filesystem Watcher**: Running / check `filesystem_watcher.pid`

## Odoo ERP Snapshot
- Check Odoo for current balance: `python odoo_mcp.py --action list_invoices --data '{"days":7}'`
- Odoo Drafts: see `Odoo_Drafts/` for local copies of pending invoices/payments

## Pending Approval Queue
Check `Pending_Approval/` for items awaiting human review.
- **Email sends/drafts**: Move approved → `Approved/`, rejected → `Rejected/`
- **Social posts** (Facebook, Instagram, X/Twitter): Separate approval per platform
- **Odoo invoices/payments**: Confirm/post requires approval
- **LinkedIn posts**: Draft for manual posting

## Social Media Status
- Platforms: Facebook, Instagram, X/Twitter, LinkedIn (draft-only)
- Recent activity summaries: see `Briefings/Social_Summary_*.md`
- Post via: `python social_facebook_mcp.py --action post --content "..." --dry-run`

## Latest Audit
See `Briefings/` for the most recent Weekly Audit.
- **Auto-generated**: Sunday nights
- **Manual trigger**: `python orchestrator.py --generate-audit`
- Includes: Revenue Summary, Completed Tasks, Bottleneck Analysis, Social Activity, Suggestions

## Quarantine & Alerts
- **Quarantine**: `Quarantine/` — tasks that failed after retries. Review and re-process manually.
- **Alerts**: `Alerts/` — critical failure notifications. Check and resolve promptly.

## Gold Tier Services
| Service | Script | Purpose |
|---------|--------|---------|
| Orchestrator | `orchestrator.py` | Central brain — claims, invokes Claude, dispatches MCPs |
| Gmail Watcher | `gmail_watcher.py` | Detects unread emails → task files |
| Filesystem Watcher | `filesystem_watcher.py` | Detects files in `watch_inbox/` |
| Email MCP | `email_mcp.py` | Send/draft emails via Gmail API |
| Odoo MCP | `odoo_mcp.py` | Draft/confirm invoices and payments |
| Facebook MCP | `social_facebook_mcp.py` | Post + fetch activity |
| Instagram MCP | `social_instagram_mcp.py` | Post + fetch activity |
| X/Twitter MCP | `social_x_mcp.py` | Post (or draft fallback) + fetch activity |
| Audit Generator | `audit_generator.py` | Weekly 5-section audit |
| Watchdog | `watchdog_monitor.py` | Process monitor + auto-restart |
| Retry Handler | `retry_handler.py` | Exponential backoff for API errors |
| Quarantine Utils | `quarantine_utils.py` | Failed task handling + alert creation |
