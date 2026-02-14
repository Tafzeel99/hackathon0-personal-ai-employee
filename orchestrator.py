# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Orchestrator: claims tasks, invokes Claude Code, handles HITL approval.
Usage: python orchestrator.py [--dry-run] [--once] [--generate-audit]"""
import argparse, json, os, re, signal, shutil, subprocess, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
from log_utils import log_event
from retry_handler import retry_call, RetryExhausted
from quarantine_utils import quarantine_task, create_alert

VAULT = Path(__file__).parent / "AI_Employee_Vault"
NEEDS, IN_PROG, PLANS = VAULT / "Needs_Action", VAULT / "In_Progress", VAULT / "Plans"
PENDING, APPROVED, REJECTED, DONE = (VAULT / d for d in ["Pending_Approval", "Approved", "Rejected", "Done"])
BRIEFINGS, SKILLS = VAULT / "Briefings", VAULT / "agent_skills"
QUARANTINE, ALERTS, ODOO_DRAFTS = VAULT / "Quarantine", VAULT / "Alerts", VAULT / "Odoo_Drafts"
PKT, MAX_ITER = timezone(timedelta(hours=5)), 50

# Domain health tracking: domain -> consecutive failure count
_domain_failures = {"email": 0, "social": 0, "erp": 0}
DOMAIN_DOWN_THRESHOLD = 3


def ensure_dirs():
    for d in [NEEDS, IN_PROG, PLANS, PENDING, APPROVED, REJECTED, DONE,
              BRIEFINGS, QUARANTINE, ALERTS, ODOO_DRAFTS]:
        d.mkdir(parents=True, exist_ok=True)


def detect_domain(text):
    """Detect which domain a task/approval belongs to."""
    t = text.lower()
    if any(k in t for k in ["odoo", "invoice", "payment", "erp", "odoo_confirm", "odoo_payment"]):
        return "erp"
    if any(k in t for k in ["facebook", "instagram", "twitter", "post_facebook",
                             "post_instagram", "post_x", "social", "linkedin"]):
        return "social"
    if any(k in t for k in ["email", "gmail", "email_send"]):
        return "email"
    return None


def is_domain_healthy(domain):
    """Check if a domain's API is considered healthy."""
    if domain is None:
        return True
    return _domain_failures.get(domain, 0) < DOMAIN_DOWN_THRESHOLD


def mark_domain_success(domain):
    if domain:
        _domain_failures[domain] = 0


def mark_domain_failure(domain):
    if domain:
        _domain_failures[domain] = _domain_failures.get(domain, 0) + 1
        if _domain_failures[domain] == DOMAIN_DOWN_THRESHOLD:
            create_alert(f"{domain.upper()} API Down",
                         f"Domain '{domain}' has failed {DOMAIN_DOWN_THRESHOLD} consecutive times.",
                         f"orchestrator/{domain}", f"Check {domain} API credentials and availability.",
                         source="orchestrator")


def claim_task():
    for f in sorted(NEEDS.glob("*.md")):
        txt = f.read_text("utf-8", errors="replace")
        domain = detect_domain(txt)
        if not is_domain_healthy(domain):
            continue
        try:
            dest = IN_PROG / f.name; shutil.move(str(f), str(dest))
            log_event("task_claimed", "orchestrator", "success", f"In_Progress/{f.name}")
            print(f"[CLAIMED] {f.name}"); return dest
        except FileNotFoundError:
            continue


def load_skills():
    return "".join(f"\n--- {s.name} ---\n{s.read_text('utf-8')}" for s in sorted(SKILLS.glob("*.md")))


def invoke_claude(task_path, dry_run):
    ref = f"In_Progress/{task_path.name}"
    if dry_run:
        log_event("claude_invoked", "orchestrator", "dry_run", ref)
        return (f"---\nobjective: Process {task_path.name}\nstatus: complete\n"
                f"task_ref: {ref}\naction_required: no\n---\n"
                "\n## Steps\n- [x] Analyzed task (dry-run)\n\nTASK_COMPLETE")
    prompt = (f"You are the AI Employee (Gold Tier). Process this task.\n\n"
              f"## Task\n{task_path.read_text('utf-8')}\n\n## Skills\n{load_skills()}\n\n"
              "Write Plan.md with frontmatter (objective, status, task_ref, action_required, "
              "hitl_type, domain) and Steps. Add Approval Required section if needed. "
              "Add LinkedIn/Social Post Draft or Odoo Operation section if relevant. "
              "End with TASK_COMPLETE.")
    output = ""
    for i in range(MAX_ITER):
        try:
            r = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=120)
            output = r.stdout
            log_event("claude_invoked", "orchestrator", "success", ref,
                      {"iteration": i + 1, "max_iter": MAX_ITER})
            if "TASK_COMPLETE" in output:
                return output
            if (DONE / task_path.name).exists():
                log_event("task_complete_file_move", "orchestrator", "success", ref,
                          {"iteration": i + 1, "method": "file_move_check"})
                return output
            prompt = f"Continue. Previous:\n{output[-2000:]}\nEnd with TASK_COMPLETE."
        except Exception as e:
            log_event("error", "orchestrator", "failure", ref,
                      {"iteration": i + 1, "error": str(e)[:200]})
            break
    log_event("loop_exhausted", "orchestrator", "failure", ref,
              {"iterations": MAX_ITER, "last_output": output[-200:]})
    create_alert("Ralph Wiggum Loop Exhausted",
                 f"Task {task_path.name} did not complete after {MAX_ITER} iterations.",
                 "orchestrator/ralph_loop",
                 "Review the task manually. Check if the task is stuck or malformed.")
    quarantine_task(task_path, f"Loop exhausted after {MAX_ITER} iterations", source="orchestrator")
    return output


def save_plan(task_path, plan_text):
    name = re.sub(r"_\d{8}_\d{6}", "", re.sub(r"^(TASK_|EMAIL_|SCHEDULED_|ODOO_|SOCIAL_)", "", task_path.stem))
    pp = PLANS / f"Plan_{name}.md"; pp.write_text(plan_text, encoding="utf-8")
    log_event("plan_created", "orchestrator", "success", f"Plans/{pp.name}")
    print(f"[PLAN] {pp.name}"); return pp


def save_odoo_draft(task_path, plan_text):
    """Save a local Markdown copy of Odoo draft to Odoo_Drafts/."""
    if "odoo" not in plan_text.lower() and "invoice" not in plan_text.lower():
        return None
    now = datetime.now(PKT)
    slug = re.sub(r"[^a-z0-9]+", "-", task_path.stem.lower())[:40]
    fname = f"OdooDraft_{now.strftime('%Y%m%d_%H%M%S')}_{slug}.md"
    path = ODOO_DRAFTS / fname
    path.write_text(f"---\ncreated: {now.isoformat()}\nsource: {task_path.name}\n---\n\n{plan_text}\n",
                    encoding="utf-8")
    log_event("odoo_draft_saved", "orchestrator", "success", f"Odoo_Drafts/{fname}")
    print(f"[ODOO_DRAFT] {fname}")
    return path


def create_approval(task_path, plan_path, plan_text):
    if "action_required: yes" not in plan_text:
        return False
    # Detect HITL type from plan text
    hitl_types = []
    for ht in ["email_send", "email_draft", "post_linkedin", "post_facebook",
               "post_instagram", "post_x", "odoo_confirm", "odoo_payment"]:
        if ht in plan_text:
            hitl_types.append(ht)
    if not hitl_types:
        hitl_types = ["email_send"]
    domain = detect_domain(plan_text) or "internal"
    now = datetime.now(PKT)
    slug = re.sub(r"[^a-z0-9]+", "-", task_path.stem.lower())[:40]
    for hitl in hitl_types:
        fn = f"APPROVE_{now.strftime('%Y%m%d_%H%M%S')}_{hitl}_{slug}.md"
        (PENDING / fn).write_text(
            f"---\naction_type: {hitl}\ntarget: see-plan\n"
            f"content_summary: \"Action from {task_path.name}\"\n"
            f"plan_ref: Plans/{plan_path.name}\ntask_ref: In_Progress/{task_path.name}\n"
            f"domain: {domain}\ncreated: {now.isoformat()}\nstatus: pending_approval\n---\n\n"
            f"{plan_text}\n", encoding="utf-8")
        log_event("approval_created", "orchestrator", "success", f"Pending_Approval/{fn}",
                  {"hitl_type": hitl, "domain": domain})
        print(f"[HITL] {fn}")
    return True


def move_to_done(*paths):
    for p in paths:
        if p and p.exists():
            shutil.move(str(p), str(DONE / p.name))


def dispatch_mcp(fpath, txt, action_type, dry_run):
    """Dispatch to the appropriate MCP based on action_type."""
    domain = detect_domain(txt)
    try:
        if action_type in ("email_send", "email_draft"):
            dispatch_email(fpath, txt, dry_run)
        elif action_type == "post_linkedin":
            log_event("post_linkedin_approved", "orchestrator", "success",
                      f"Approved/{fpath.name}", "Ready for manual posting")
            print(f"[LINKEDIN] Approved: {fpath.name}")
        elif action_type in ("odoo_confirm", "odoo_payment"):
            dispatch_odoo(fpath, txt, action_type, dry_run)
        elif action_type in ("post_facebook", "post_instagram", "post_x"):
            dispatch_social(fpath, txt, action_type, dry_run)
        else:
            log_event("unknown_action", "orchestrator", "failure",
                      f"Approved/{fpath.name}", {"action_type": action_type})
        mark_domain_success(domain)
    except (RetryExhausted, Exception) as e:
        mark_domain_failure(domain)
        task_ref_m = re.search(r"task_ref:\s*(.+)", txt)
        task_ref = task_ref_m.group(1).strip() if task_ref_m else None
        if task_ref:
            task_path = VAULT / task_ref
            if task_path.exists():
                quarantine_task(task_path, str(e), source="orchestrator")
        create_alert(f"{action_type} dispatch failed",
                     f"Failed to dispatch {action_type} for {fpath.name}: {e}",
                     f"orchestrator/{action_type}",
                     f"Check {domain} API credentials and connectivity.",
                     source="orchestrator")
        log_event("dispatch_failed", "orchestrator", "failure",
                  f"Approved/{fpath.name}", {"error": str(e)[:200], "action_type": action_type})


def dispatch_email(fpath, txt, dry_run):
    to_m = re.search(r"\*\*To\*\*:\s*(.+)", txt)
    subj_m = re.search(r"\*\*Subject\*\*:\s*(.+)", txt)
    body_m = re.search(r"\*\*Body\*\*:\s*\n([\s\S]+?)(?=\n##|\n---|\Z)", txt)
    tgt = re.search(r"target:\s*(.+)", txt)
    to = to_m.group(1).strip() if to_m else (tgt.group(1).strip() if tgt else "unknown")
    subj = subj_m.group(1).strip() if subj_m else "No Subject"
    body = body_m.group(1).strip() if body_m else ""
    cmd = [sys.executable, "email_mcp.py", "--to", to, "--subject", subj, "--body", body]
    if "email_draft" in txt:
        cmd.append("--draft-only")
    if dry_run:
        cmd.append("--dry-run")

    def _run():
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout) if r.stdout.strip() else {"status": "error"}
        if res.get("status") == "error":
            raise RuntimeError(f"Email MCP error: {res}")
        return res

    res = retry_call(_run, source="orchestrator", task_ref=f"Approved/{fpath.name}")
    log_event("email_dispatched", "orchestrator", res.get("status", "success"),
              f"Approved/{fpath.name}", {"to": to, "mcp_params": {"subject": subj}})
    print(f"[EMAIL] {res.get('status', 'success')}: {to}")


def dispatch_odoo(fpath, txt, action_type, dry_run):
    """Dispatch Odoo confirm/payment action via odoo_mcp.py."""
    action_map = {"odoo_confirm": "confirm_invoice", "odoo_payment": "confirm_payment"}
    action = action_map.get(action_type, "confirm_invoice")
    data_m = re.search(r"odoo_data:\s*(\{.+?\})", txt, re.DOTALL)
    data_json = data_m.group(1) if data_m else "{}"
    cmd = [sys.executable, "odoo_mcp.py", "--action", action, "--data", data_json]
    if dry_run:
        cmd.append("--dry-run")

    def _run():
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout) if r.stdout.strip() else {"status": "error"}
        if res.get("status") == "error":
            raise RuntimeError(f"Odoo MCP error: {res}")
        return res

    res = retry_call(_run, source="orchestrator", task_ref=f"Approved/{fpath.name}")
    log_event("odoo_dispatched", "orchestrator", res.get("status", "success"),
              f"Approved/{fpath.name}",
              {"action": action, "odoo_record_id": res.get("record_id"),
               "mcp_params": {"action": action, "data": data_json[:100]}})
    print(f"[ODOO] {action}: {res.get('status', 'success')}")


def dispatch_social(fpath, txt, action_type, dry_run):
    """Dispatch social post via the appropriate social MCP."""
    platform_map = {"post_facebook": "social_facebook_mcp.py",
                    "post_instagram": "social_instagram_mcp.py",
                    "post_x": "social_x_mcp.py"}
    script = platform_map.get(action_type)
    if not script:
        return
    content_m = re.search(r"(?:post_text|content|draft):\s*[\"']?(.+?)(?:[\"']?\n|$)", txt, re.DOTALL)
    content = content_m.group(1).strip() if content_m else ""
    if not content:
        body_m = re.search(r"## (?:Post|Draft|Content)\s*\n([\s\S]+?)(?=\n##|\n---|\Z)", txt)
        content = body_m.group(1).strip() if body_m else "No content"
    cmd = [sys.executable, script, "--action", "post", "--content", content]
    if dry_run:
        cmd.append("--dry-run")

    def _run():
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout) if r.stdout.strip() else {"status": "error"}
        if res.get("status") == "error":
            raise RuntimeError(f"Social MCP error: {res}")
        return res

    res = retry_call(_run, source="orchestrator", task_ref=f"Approved/{fpath.name}")
    log_event("social_dispatched", "orchestrator", res.get("status", "success"),
              f"Approved/{fpath.name}",
              {"platform": action_type, "social_post_id": res.get("post_id"),
               "mcp_params": {"action": "post", "content": content[:50]}})
    print(f"[SOCIAL] {action_type}: {res.get('status', 'success')}")


def handle_approved(dry_run=False):
    for f in APPROVED.glob("*.md"):
        txt = f.read_text("utf-8")
        # Detect action type from frontmatter
        at_m = re.search(r"action_type:\s*(\S+)", txt)
        action_type = at_m.group(1) if at_m else "unknown"
        dispatch_mcp(f, txt, action_type, dry_run)
        shutil.move(str(f), str(DONE / f.name))


def handle_rejected():
    for f in REJECTED.glob("*.md"):
        txt = f.read_text("utf-8")
        at_m = re.search(r"action_type:\s*(\S+)", txt)
        action_type = at_m.group(1) if at_m else ""
        # Domain-specific rejection cleanup
        if action_type in ("odoo_confirm", "odoo_payment"):
            log_event("odoo_rejection", "orchestrator", "success", f"Rejected/{f.name}",
                      "Odoo draft should be cancelled manually or via odoo_mcp --action cancel_invoice")
        log_event("action_rejected", "orchestrator", "success", f"Rejected/{f.name}",
                  {"action_type": action_type})
        print(f"[REJECTED] {f.name}")
        shutil.move(str(f), str(DONE / f.name))


def detect_multi_step(plan_text):
    """Detect if a plan contains multiple sequential HITL steps."""
    hitl_types = []
    for ht in ["odoo_confirm", "odoo_payment", "post_facebook",
               "post_instagram", "post_x", "post_linkedin", "email_send"]:
        if ht in plan_text:
            hitl_types.append(ht)
    return hitl_types if len(hitl_types) > 1 else []


def process_task(task_path, dry_run):
    plan_text = invoke_claude(task_path, dry_run)
    if not plan_text or task_path.parent == QUARANTINE:
        return  # Task was quarantined during invoke_claude
    plan_path = save_plan(task_path, plan_text)
    save_odoo_draft(task_path, plan_text)
    multi_steps = detect_multi_step(plan_text)
    if multi_steps:
        # Multi-step: create state tracking file
        state_path = IN_PROG / f".state_{task_path.stem}.json"
        state = {"task": task_path.name, "steps": multi_steps,
                 "current_step": 0, "completed_steps": []}
        state_path.write_text(json.dumps(state), encoding="utf-8")
        log_event("multi_step_detected", "orchestrator", "success",
                  f"In_Progress/{task_path.name}",
                  {"steps": multi_steps, "step_count": len(multi_steps)})
    if not create_approval(task_path, plan_path, plan_text):
        move_to_done(task_path, plan_path)
        print(f"[DONE] {task_path.name}")


def fetch_social_activity(dry_run):
    """Fetch recent activity from all social platforms and write a combined summary."""
    now = datetime.now(PKT)
    fname = f"Social_Summary_{now.date().isoformat()}.md"
    if (BRIEFINGS / fname).exists():
        return  # Already generated today
    summaries = {}
    for platform, script in [("facebook", "social_facebook_mcp.py"),
                             ("instagram", "social_instagram_mcp.py"),
                             ("x", "social_x_mcp.py")]:
        cmd = [sys.executable, script, "--action", "fetch_activity"]
        if dry_run:
            cmd.append("--dry-run")
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if r.stdout.strip():
                summaries[platform] = json.loads(r.stdout)
        except Exception as e:
            log_event("social_fetch_error", "orchestrator", "failure",
                      details={"platform": platform, "error": str(e)[:200]})
    # Write combined summary
    lines = [f"---\ntype: social_summary\ngenerated: {now.isoformat()}\n---\n",
             f"# Social Activity Summary — {now.date().isoformat()}\n",
             "| Platform | Posts | Likes | Comments | Shares/RTs |",
             "|----------|-------|-------|----------|------------|"]
    for p, data in summaries.items():
        s = data.get("summary", {})
        posts = s.get("post_count", s.get("media_count", s.get("tweet_count", 0)))
        likes = s.get("total_likes", 0)
        comments = s.get("total_comments", 0)
        shares = s.get("total_retweets", "N/A")
        lines.append(f"| {p.title()} | {posts} | {likes} | {comments} | {shares} |")
    lines.append("")
    (BRIEFINGS / fname).write_text("\n".join(lines), encoding="utf-8")
    log_event("social_summary_generated", "orchestrator", "success",
              details=f"Briefings/{fname}")
    print(f"[SOCIAL_SUMMARY] {fname}")


def check_weekly_audit(dry_run):
    now = datetime.now(PKT)
    # Trigger on Sunday (weekday 6) or via --generate-audit flag
    if now.weekday() == 6 and not (BRIEFINGS / f"Audit_{now.date().isoformat()}.md").exists():
        print("[AUDIT] Sunday — generating weekly audit.")
        cmd = [sys.executable, "audit_generator.py", "--generate-audit"]
        if dry_run:
            cmd.append("--dry-run")
        subprocess.run(cmd)


PID_FILE = Path(__file__).parent / "orchestrator.pid"


def cleanup(signum=None, frame=None):
    PID_FILE.unlink(missing_ok=True)
    print("\nOrchestrator stopped.")
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser(description="Orchestrator – Gold Tier")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--generate-audit", action="store_true", help="Run weekly audit now")
    ap.add_argument("--once", action="store_true", help="One cycle then exit")
    args = ap.parse_args()
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"
    ensure_dirs()
    if args.generate_audit:
        cmd = [sys.executable, "audit_generator.py", "--generate-audit"]
        if dry_run:
            cmd.append("--dry-run")
        subprocess.run(cmd)
        return
    # PID file management
    PID_FILE.write_text(str(os.getpid()))
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"Orchestrator started ({mode}).")
    log_event("watcher_started", "orchestrator", "success", details=mode)
    try:
        while True:
            task = claim_task()
            if task:
                process_task(task, dry_run)
            handle_approved(dry_run)
            handle_rejected()
            check_weekly_audit(dry_run)
            if args.once:
                break
            time.sleep(5)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
