# Silver Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""CEO Briefing generator: summarises Done/ tasks, pending items, suggestions.
Usage: python briefing_generator.py [--dry-run]"""
import argparse, os, re
from datetime import datetime, timezone, timedelta
from pathlib import Path
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
from log_utils import log_event
VAULT = Path(__file__).parent / "AI_Employee_Vault"
DONE, NEEDS, IN_PROG, PENDING = VAULT / "Done", VAULT / "Needs_Action", VAULT / "In_Progress", VAULT / "Pending_Approval"
BRIEFINGS, PKT = VAULT / "Briefings", timezone(timedelta(hours=5))

def parse_frontmatter(path):
    text = path.read_text("utf-8", errors="replace")
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m: return {}
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip().strip('"').strip("'")
    return fields

def collect_done_tasks(period_start, period_end):
    tasks = {"email_inbound": [], "file_drop": [], "scheduled": []}
    if not DONE.exists(): return tasks, 0
    count = 0
    for f in sorted(DONE.glob("*.md")):
        fm = parse_frontmatter(f)
        objective = fm.get("objective", fm.get("subject", f.stem))
        status = fm.get("status", "complete")
        try: dt = datetime.fromisoformat(fm.get("created", "").replace("Z", "+00:00"))
        except (ValueError, AttributeError): dt = datetime.fromtimestamp(f.stat().st_mtime, tz=PKT)
        if period_start <= dt.date() <= period_end:
            bucket = fm.get("type", "file_drop")
            if bucket not in tasks: bucket = "file_drop"
            mark = "completed" if status in ("complete", "completed") else status
            tasks[bucket].append({"date": dt.strftime("%Y-%m-%d"), "summary": objective, "status": mark})
            count += 1
    return tasks, count

def collect_pending():
    items, now = [], datetime.now(PKT)
    for folder, label in [(NEEDS, "Needs_Action"), (IN_PROG, "In_Progress"), (PENDING, "Pending_Approval")]:
        if not folder.exists(): continue
        for f in sorted(folder.glob("*.md")):
            fm = parse_frontmatter(f)
            try:
                dt = datetime.fromisoformat(fm.get("created", "").replace("Z", "+00:00"))
                age = (now - dt).days
            except (ValueError, AttributeError): age = 0
            summary = fm.get("subject", fm.get("objective", f.stem))
            items.append(f"- {f.name[:5].rstrip('_').upper()}: {summary} ({age}d old, in {label})")
    return items

def generate_suggestion(tasks, pending_count):
    email_count, total = len(tasks.get("email_inbound", [])), sum(len(v) for v in tasks.values())
    if email_count > total * 0.6 and total > 3:
        return f"You received {email_count} email tasks out of {total}. Consider email filters."
    if pending_count > 3:
        return f"{pending_count} items still pending. Consider a mid-week triage."
    if total == 0:
        return "No completed tasks this period. Check if watchers and orchestrator are running."
    return "Task volume looks healthy. Keep the current workflow cadence."

def generate_briefing(dry_run=False):
    BRIEFINGS.mkdir(parents=True, exist_ok=True)
    now, period_end = datetime.now(PKT), datetime.now(PKT).date()
    period_start = period_end - timedelta(days=7)
    fname = f"Monday_{period_end.isoformat()}.md"
    tasks, task_count = collect_done_tasks(period_start, period_end)
    pending = collect_pending()
    suggestion = generate_suggestion(tasks, len(pending))
    # Build sections
    lines = [f"## Completed Tasks ({task_count})\n"]
    for label, key in [("Email Tasks", "email_inbound"), ("File Drop Tasks", "file_drop"), ("Scheduled Tasks", "scheduled")]:
        items = tasks[key]
        lines.append(f"### {label} ({len(items)})")
        for t in items: lines.append(f"- {t['date']}: {t['summary']} ({t['status']})")
        if not items: lines.append("- (none)")
        lines.append("")
    lines += ["", f"## Pending Items ({len(pending)})\n"]
    lines.extend(pending if pending else ["- (none)"])
    lines += ["", f"## Proactive Suggestion\n", suggestion]
    body = "\n".join(lines)
    content = (f"---\ntype: ceo_briefing\nperiod_start: {period_start.isoformat()}\n"
               f"period_end: {period_end.isoformat()}\ngenerated: {now.isoformat()}\n"
               f"task_count: {task_count}\n---\n\n{body}\n")
    out_path = BRIEFINGS / fname
    if dry_run:
        print(f"[DRY-RUN] Would write: {out_path}\n{content}")
        log_event("briefing_generated", "briefing_generator", "dry_run",
                  details=f"task_count={task_count}, path={fname}")
    else:
        out_path.write_text(content, encoding="utf-8")
        log_event("briefing_generated", "briefing_generator", "success",
                  details=f"task_count={task_count}, path={fname}")
        print(f"[BRIEFING] Generated: {out_path}")
    return out_path

def main():
    ap = argparse.ArgumentParser(description="CEO Briefing Generator – Silver Tier")
    ap.add_argument("--dry-run", action="store_true", help="Print without writing")
    args = ap.parse_args()
    generate_briefing(args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true")

if __name__ == "__main__":
    main()
