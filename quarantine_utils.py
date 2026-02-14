# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Utilities for quarantining failed tasks and creating alert files."""
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from log_utils import log_event

VAULT = Path(__file__).parent / "AI_Employee_Vault"
QUARANTINE = VAULT / "Quarantine"
ALERTS = VAULT / "Alerts"
PKT = timezone(timedelta(hours=5))


def quarantine_task(task_path, error_msg, source="quarantine_utils"):
    """Move a task file to Quarantine/ with error details prepended."""
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    dest = QUARANTINE / task_path.name
    content = task_path.read_text("utf-8") if task_path.exists() else ""
    now = datetime.now(PKT).isoformat()
    # Inject error details after existing frontmatter
    error_block = (f"\n<!-- QUARANTINED: {now} -->\n"
                   f"<!-- ERROR: {error_msg[:300]} -->\n")
    if "---" in content:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            parts[1] = parts[1].rstrip() + f"\nstatus: quarantined\nquarantined: {now}\n"
            content = "---".join(parts)
    content = content + error_block
    dest.write_text(content, encoding="utf-8")
    if task_path.exists() and task_path.parent != QUARANTINE:
        task_path.unlink()
    log_event("task_quarantined", source, "failure",
              f"Quarantine/{task_path.name}",
              {"error": error_msg[:200], "quarantined_at": now})
    return dest


def create_alert(title, description, component, remediation, source="quarantine_utils"):
    """Create a human-readable alert file in Alerts/."""
    ALERTS.mkdir(parents=True, exist_ok=True)
    now = datetime.now(PKT)
    slug = title.lower().replace(" ", "-")[:40]
    fname = f"ALERT_{now.strftime('%Y%m%d_%H%M%S')}_{slug}.md"
    path = ALERTS / fname
    path.write_text(
        f"---\ntype: alert\ncreated: {now.isoformat()}\n"
        f"component: {component}\nseverity: critical\nstatus: open\n---\n\n"
        f"# Alert: {title}\n\n"
        f"**Component**: {component}\n"
        f"**Time**: {now.isoformat()}\n\n"
        f"## Description\n\n{description}\n\n"
        f"## Suggested Remediation\n\n{remediation}\n",
        encoding="utf-8")
    log_event("alert_created", source, "success",
              f"Alerts/{fname}", {"title": title, "component": component})
    return path
