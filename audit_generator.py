# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Weekly audit generator: comprehensive cross-domain briefing with 5 sections.
Usage: python audit_generator.py [--generate-audit] [--dry-run]"""
import argparse, json, os, re, subprocess, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
from log_utils import log_event

VAULT = Path(__file__).parent / "AI_Employee_Vault"
DONE, NEEDS, IN_PROG, PENDING = VAULT / "Done", VAULT / "Needs_Action", VAULT / "In_Progress", VAULT / "Pending_Approval"
BRIEFINGS, QUARANTINE = VAULT / "Briefings", VAULT / "Quarantine"
PKT = timezone(timedelta(hours=5))


def parse_frontmatter(path):
    text = path.read_text("utf-8", errors="replace")
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip().strip('"').strip("'")
    return fields


# --- Section 1: Revenue Summary ---
def collect_odoo_data(dry_run):
    """Fetch Odoo invoice/payment data for revenue summary."""
    invoices, payments = [], []
    for action, target in [("list_invoices", invoices), ("list_payments", payments)]:
        cmd = [sys.executable, "odoo_mcp.py", "--action", action, "--data", '{"days": 7}']
        if dry_run:
            cmd.append("--dry-run")
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if r.stdout.strip():
                data = json.loads(r.stdout)
                if action == "list_invoices":
                    invoices = data.get("invoices", [])
                else:
                    payments = data.get("payments", [])
        except Exception:
            pass
    return invoices, payments


def build_revenue_section(invoices, payments):
    total_invoiced = sum(float(i.get("amount_total", 0)) for i in invoices)
    total_paid = sum(float(p.get("amount", 0)) for p in payments)
    outstanding = total_invoiced - total_paid
    if not invoices and not payments:
        return ("## 1. Revenue Summary\n\n"
                "No transactions this period.\n")
    return (f"## 1. Revenue Summary\n\n"
            f"| Metric | Amount (PKR) | Count |\n"
            f"|--------|-------------|-------|\n"
            f"| Total Invoiced | {total_invoiced:,.0f} | {len(invoices)} |\n"
            f"| Total Paid | {total_paid:,.0f} | {len(payments)} |\n"
            f"| Outstanding | {outstanding:,.0f} | — |\n")


# --- Section 2: Completed Tasks ---
def collect_done_tasks(period_start, period_end):
    domains = {"email": [], "social": [], "erp": [], "internal": []}
    if not DONE.exists():
        return domains, 0
    count = 0
    for f in sorted(DONE.glob("*.md")):
        fm = parse_frontmatter(f)
        try:
            dt = datetime.fromisoformat(fm.get("created", "").replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            dt = datetime.fromtimestamp(f.stat().st_mtime, tz=PKT)
        if period_start <= dt.date() <= period_end:
            domain = fm.get("domain", "internal")
            if domain not in domains:
                domain = "internal"
            summary = fm.get("objective", fm.get("subject", f.stem))
            domains[domain].append({"date": dt.strftime("%Y-%m-%d"), "summary": summary})
            count += 1
    return domains, count


def build_tasks_section(domains, total):
    lines = [f"## 2. Completed Tasks ({total})\n"]
    for label, key in [("Email", "email"), ("Social", "social"),
                       ("ERP/Odoo", "erp"), ("File/Internal", "internal")]:
        items = domains[key]
        lines.append(f"### {label} ({len(items)})")
        for t in items:
            lines.append(f"- {t['date']}: {t['summary']}")
        if not items:
            lines.append("- (none)")
        lines.append("")
    return "\n".join(lines)


# --- Section 3: Bottleneck Analysis ---
def build_bottleneck_section():
    lines = ["## 3. Bottleneck Analysis\n"]
    now = datetime.now(PKT)
    # Stuck approvals (>48h in Pending_Approval)
    stuck = []
    if PENDING.exists():
        for f in PENDING.glob("*.md"):
            fm = parse_frontmatter(f)
            try:
                dt = datetime.fromisoformat(fm.get("created", "").replace("Z", "+00:00"))
                age_h = (now - dt).total_seconds() / 3600
                if age_h > 48:
                    stuck.append(f"- {f.name} — waiting {age_h:.0f}h")
            except (ValueError, AttributeError):
                pass
    lines.append(f"### Stuck Approvals (>48h): {len(stuck)}")
    lines.extend(stuck if stuck else ["- (none)"])
    lines.append("")
    # Queue depth
    needs_count = len(list(NEEDS.glob("*.md"))) if NEEDS.exists() else 0
    in_prog_count = len(list(IN_PROG.glob("*.md"))) if IN_PROG.exists() else 0
    quarantine_count = len(list(QUARANTINE.glob("*.md"))) if QUARANTINE.exists() else 0
    lines.append(f"### Queue Depth")
    lines.append(f"- Needs_Action: {needs_count}")
    lines.append(f"- In_Progress: {in_prog_count}")
    lines.append(f"- Quarantine: {quarantine_count}")
    lines.append("")
    return "\n".join(lines)


# --- Section 4: Social Activity Summary ---
def build_social_section():
    lines = ["## 4. Social Activity Summary\n"]
    # Find most recent Social_Summary file
    summaries = sorted(BRIEFINGS.glob("Social_Summary_*.md"), reverse=True)
    if summaries:
        latest = summaries[0]
        content = latest.read_text("utf-8", errors="replace")
        lines.append(f"*Source: {latest.name}*\n")
        # Extract table if present
        for line in content.splitlines():
            if line.startswith("|") or line.startswith("# "):
                lines.append(line)
    else:
        lines.append("No social activity data for this period.")
    lines.append("")
    return "\n".join(lines)


# --- Section 5: Proactive Suggestions ---
def build_suggestions(domains, total, invoices, stuck_count, quarantine_count):
    lines = ["## 5. Proactive Suggestions\n"]
    suggestions = []
    email_count = len(domains.get("email", []))
    if email_count > total * 0.6 and total > 3:
        suggestions.append(f"- **Email overload**: {email_count}/{total} tasks are emails. "
                           "Consider inbox filters or auto-categorization rules.")
    if stuck_count > 0:
        suggestions.append(f"- **Approval backlog**: {stuck_count} items waiting >48h. "
                           "Schedule a mid-week triage session.")
    if quarantine_count > 0:
        suggestions.append(f"- **Quarantined tasks**: {quarantine_count} tasks in Quarantine/. "
                           "Review error details and check API connectivity.")
    if not invoices:
        suggestions.append("- **No revenue activity**: No invoices this week. "
                           "Consider outreach or follow-up with pending clients.")
    if total == 0:
        suggestions.append("- **No activity**: No completed tasks. "
                           "Verify watchers and orchestrator are running.")
    if not suggestions:
        suggestions.append("- Task volume and operations look healthy. "
                           "Keep the current workflow cadence.")
    lines.extend(suggestions)
    lines.append("")
    return "\n".join(lines)


def generate_audit(dry_run=False):
    BRIEFINGS.mkdir(parents=True, exist_ok=True)
    now = datetime.now(PKT)
    period_end = now.date()
    period_start = period_end - timedelta(days=7)
    fname = f"Audit_{period_end.isoformat()}.md"

    # Collect data
    invoices, payments = collect_odoo_data(dry_run)
    domains, task_count = collect_done_tasks(period_start, period_end)
    stuck_count = len([1 for f in (PENDING.glob("*.md") if PENDING.exists() else [])
                       if parse_frontmatter(f).get("created")])
    quarantine_count = len(list(QUARANTINE.glob("*.md"))) if QUARANTINE.exists() else 0
    revenue_total = sum(float(i.get("amount_total", 0)) for i in invoices)

    # Build sections
    rev = build_revenue_section(invoices, payments)
    tasks = build_tasks_section(domains, task_count)
    bottleneck = build_bottleneck_section()
    social = build_social_section()
    suggestions = build_suggestions(domains, task_count, invoices, stuck_count, quarantine_count)

    content = (f"---\ntype: weekly_audit\nperiod_start: {period_start.isoformat()}\n"
               f"period_end: {period_end.isoformat()}\ngenerated: {now.isoformat()}\n"
               f"task_count: {task_count}\nrevenue_total: {revenue_total}\n---\n\n"
               f"# Weekly Audit — {period_start} to {period_end}\n\n"
               f"{rev}\n{tasks}\n{bottleneck}\n{social}\n{suggestions}")

    out_path = BRIEFINGS / fname
    if dry_run:
        print(f"[DRY-RUN] Would write: {out_path}\n{content}")
        log_event("audit_generated", "audit_generator", "dry_run",
                  details={"task_count": task_count, "revenue_total": revenue_total, "path": fname})
    else:
        out_path.write_text(content, encoding="utf-8")
        log_event("audit_generated", "audit_generator", "success",
                  details={"task_count": task_count, "revenue_total": revenue_total, "path": fname})
        print(f"[AUDIT] Generated: {out_path}")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Audit Generator – Gold Tier")
    ap.add_argument("--generate-audit", action="store_true", help="Generate weekly audit")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"
    generate_audit(dry_run)


if __name__ == "__main__":
    main()
