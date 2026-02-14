# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Shared JSONL logging utility for all Gold Tier scripts."""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Vault path — all scripts use this
VAULT_DIR = Path(__file__).parent / "AI_Employee_Vault"
LOGS_DIR = VAULT_DIR / "Logs"

# Timezone offset for Karachi (PKT = UTC+5)
PKT = timezone(timedelta(hours=5))


def log_event(action, source, result, task_ref=None, details=None):
    """Append a structured JSON log entry to today's log file.

    Args:
        action: Event type from the action vocabulary (e.g., 'email_detected')
        source: Script name that generated this entry (e.g., 'gmail_watcher')
        result: One of 'success', 'failure', 'dry_run', 'skipped'
        task_ref: Optional relative path to related task file
        details: Optional string or dict. Strings are capped at 500 chars.
                 Dicts may include Gold fields: mcp_params, response_snippet,
                 odoo_record_id, social_post_id, retry_count.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(PKT)
    log_file = LOGS_DIR / f"{now.strftime('%Y-%m-%d')}.json"

    entry = {
        "timestamp": now.isoformat(),
        "action": action,
        "source": source,
        "result": result,
    }
    if task_ref:
        entry["task_ref"] = task_ref
    if details is not None:
        if isinstance(details, dict):
            entry["details"] = details
        else:
            entry["details"] = str(details)[:500]

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
