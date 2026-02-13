# Silver Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Orchestrator: claims tasks, invokes Claude Code, handles HITL approval.
Usage: python orchestrator.py [--dry-run] [--once] [--generate-briefing]"""
import argparse, json, os, re, shutil, subprocess, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
from log_utils import log_event
VAULT = Path(__file__).parent / "AI_Employee_Vault"
NEEDS, IN_PROG, PLANS = VAULT / "Needs_Action", VAULT / "In_Progress", VAULT / "Plans"
PENDING, APPROVED, REJECTED, DONE = (VAULT / d for d in ["Pending_Approval", "Approved", "Rejected", "Done"])
BRIEFINGS, SKILLS = VAULT / "Briefings", VAULT / "agent_skills"
PKT, MAX_ITER = timezone(timedelta(hours=5)), 20

def ensure_dirs():
    for d in [NEEDS, IN_PROG, PLANS, PENDING, APPROVED, REJECTED, DONE, BRIEFINGS]:
        d.mkdir(parents=True, exist_ok=True)

def claim_task():
    for f in sorted(NEEDS.glob("*.md")):
        try:
            dest = IN_PROG / f.name; shutil.move(str(f), str(dest))
            log_event("task_claimed", "orchestrator", "success", f"In_Progress/{f.name}")
            print(f"[CLAIMED] {f.name}"); return dest
        except FileNotFoundError: continue

def load_skills():
    return "".join(f"\n--- {s.name} ---\n{s.read_text('utf-8')}" for s in sorted(SKILLS.glob("*.md")))

def invoke_claude(task_path, dry_run):
    ref = f"In_Progress/{task_path.name}"
    if dry_run:
        log_event("claude_invoked", "orchestrator", "dry_run", ref)
        return (f"---\nobjective: Process {task_path.name}\nstatus: complete\n"
                f"task_ref: {ref}\naction_required: no\n---\n"
                "\n## Steps\n- [x] Analyzed task (dry-run)\n\nTASK_COMPLETE")
    prompt = (f"You are the AI Employee (Silver Tier). Process this task.\n\n"
              f"## Task\n{task_path.read_text('utf-8')}\n\n## Skills\n{load_skills()}\n\n"
              "Write Plan.md with frontmatter (objective, status, task_ref, action_required) "
              "and Steps. Add Approval Required section if needed. "
              "Add LinkedIn Post Draft if relevant. End with TASK_COMPLETE.")
    output = ""
    for i in range(MAX_ITER):
        try:
            r = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=120)
            output = r.stdout
            log_event("claude_invoked", "orchestrator", "success", ref, f"Iter {i+1}/{MAX_ITER}")
            if "TASK_COMPLETE" in output: return output
            prompt = f"Continue. Previous:\n{output[-2000:]}\nEnd with TASK_COMPLETE."
        except Exception as e:
            log_event("error", "orchestrator", "failure", details=f"Claude: {e}"); break
    log_event("loop_warning", "orchestrator", "failure", ref, f"Hit {MAX_ITER} iterations")
    return output

def save_plan(task_path, plan_text):
    name = re.sub(r"_\d{8}_\d{6}", "", re.sub(r"^(TASK_|EMAIL_|SCHEDULED_)", "", task_path.stem))
    pp = PLANS / f"Plan_{name}.md"; pp.write_text(plan_text, encoding="utf-8")
    log_event("plan_created", "orchestrator", "success", f"Plans/{pp.name}")
    print(f"[PLAN] {pp.name}"); return pp

def create_approval(task_path, plan_path, plan_text):
    if "action_required: yes" not in plan_text: return False
    hitl = "email_send" if "email_send" in plan_text else "post_linkedin"
    now, slug = datetime.now(PKT), re.sub(r"[^a-z0-9]+", "-", task_path.stem.lower())[:40]
    fn = f"APPROVE_{now.strftime('%Y%m%d_%H%M%S')}_{slug}.md"
    (PENDING / fn).write_text(
        f"---\naction_type: {hitl}\ntarget: see-plan\n"
        f"content_summary: \"Action from {task_path.name}\"\n"
        f"plan_ref: Plans/{plan_path.name}\ntask_ref: In_Progress/{task_path.name}\n"
        f"created: {now.isoformat()}\nstatus: pending_approval\n---\n\n{plan_text}\n", encoding="utf-8")
    log_event("approval_created", "orchestrator", "success", f"Pending_Approval/{fn}")
    print(f"[HITL] {fn}"); return True

def move_to_done(*paths):
    for p in paths:
        if p and p.exists(): shutil.move(str(p), str(DONE / p.name))

def dispatch_email(fpath, txt, dry_run):
    to_m, subj_m = re.search(r"\*\*To\*\*:\s*(.+)", txt), re.search(r"\*\*Subject\*\*:\s*(.+)", txt)
    body_m, tgt = re.search(r"\*\*Body\*\*:\s*\n([\s\S]+?)(?=\n##|\n---|\Z)", txt), re.search(r"target:\s*(.+)", txt)
    to = to_m.group(1).strip() if to_m else (tgt.group(1).strip() if tgt else "unknown")
    subj, body = (subj_m.group(1).strip() if subj_m else "No Subject"), (body_m.group(1).strip() if body_m else "")
    cmd = [sys.executable, "email_mcp.py", "--to", to, "--subject", subj, "--body", body]
    if "email_draft" in txt: cmd.append("--draft-only")
    if dry_run: cmd.append("--dry-run")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout) if r.stdout.strip() else {"status": "error"}
        log_event("email_dispatched", "orchestrator", res.get("status", "error"),
                  f"Approved/{fpath.name}", f"To: {to}")
        print(f"[EMAIL] {res.get('status','error')}: {to}")
    except Exception as e:
        log_event("email_dispatch_failed", "orchestrator", "failure", f"Approved/{fpath.name}", str(e))

def handle_approved(dry_run=False):
    for f in APPROVED.glob("*.md"):
        txt = f.read_text("utf-8")
        if "email_send" in txt or "email_draft" in txt: dispatch_email(f, txt, dry_run)
        elif "post_linkedin" in txt:
            log_event("post_linkedin_approved", "orchestrator", "success", f"Approved/{f.name}", "Ready for manual posting")
            print(f"[LINKEDIN] Approved: {f.name}")
        shutil.move(str(f), str(DONE / f.name))

def handle_rejected():
    for f in REJECTED.glob("*.md"):
        log_event("action_rejected", "orchestrator", "success", f"Rejected/{f.name}")
        print(f"[REJECTED] {f.name}"); shutil.move(str(f), str(DONE / f.name))

def process_task(task_path, dry_run):
    plan_text = invoke_claude(task_path, dry_run)
    plan_path = save_plan(task_path, plan_text)
    if not create_approval(task_path, plan_path, plan_text):
        move_to_done(task_path, plan_path); print(f"[DONE] {task_path.name}")

def check_monday_briefing(dry_run):
    now = datetime.now(PKT)
    if now.weekday() == 0 and not (BRIEFINGS / f"Monday_{now.date().isoformat()}.md").exists():
        print("[BRIEFING] Monday — generating weekly CEO Briefing.")
        cmd = [sys.executable, "briefing_generator.py"]
        if dry_run: cmd.append("--dry-run")
        subprocess.run(cmd)

def main():
    ap = argparse.ArgumentParser(description="Orchestrator – Silver Tier")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--generate-briefing", action="store_true")
    ap.add_argument("--once", action="store_true", help="One cycle then exit")
    args = ap.parse_args()
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"
    ensure_dirs()
    if args.generate_briefing:
        subprocess.run([sys.executable, "briefing_generator.py"] + (["--dry-run"] if dry_run else [])); return
    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"Orchestrator started ({mode})."); log_event("watcher_started", "orchestrator", "success", details=mode)
    try:
        while True:
            task = claim_task()
            if task: process_task(task, dry_run)
            handle_approved(dry_run); handle_rejected(); check_monday_briefing(dry_run)
            if args.once: break
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nOrchestrator stopped.")

if __name__ == "__main__":
    main()
