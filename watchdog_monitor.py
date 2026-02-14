# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Watchdog: monitors watcher/orchestrator processes, restarts if crashed.
Usage: python watchdog_monitor.py [--dry-run] [--processes <json-list>]"""
import argparse, json, os, signal, subprocess, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from log_utils import log_event
from quarantine_utils import create_alert

PKT = timezone(timedelta(hours=5))
PID_DIR = Path(__file__).parent
POLL_INTERVAL = 15  # seconds
MAX_RESTARTS_PER_WINDOW = 3
RESTART_WINDOW = 300  # 5 minutes

DEFAULT_PROCESSES = [
    {"name": "filesystem_watcher", "cmd": [sys.executable, "filesystem_watcher.py"]},
    {"name": "gmail_watcher", "cmd": [sys.executable, "gmail_watcher.py"]},
    {"name": "orchestrator", "cmd": [sys.executable, "orchestrator.py"]},
]

# Track restart history: name -> list of timestamps
_restart_history = {}


def read_pid(name):
    """Read PID from .pid file."""
    pid_file = PID_DIR / f"{name}.pid"
    if pid_file.exists():
        try:
            return int(pid_file.read_text().strip())
        except (ValueError, OSError):
            return None
    return None


def is_running(pid):
    """Check if a process with given PID is alive."""
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def should_restart(name):
    """Check if we're within restart limits (prevent restart loops)."""
    now = time.time()
    history = _restart_history.get(name, [])
    # Clean old entries outside the window
    history = [t for t in history if now - t < RESTART_WINDOW]
    _restart_history[name] = history
    return len(history) < MAX_RESTARTS_PER_WINDOW


def restart_process(proc_info, dry_run=False):
    """Restart a process and update PID file."""
    name = proc_info["name"]
    cmd = proc_info["cmd"]
    now = datetime.now(PKT)
    if not should_restart(name):
        msg = f"{name} exceeded {MAX_RESTARTS_PER_WINDOW} restarts in {RESTART_WINDOW}s"
        create_alert(f"{name} restart loop", msg, f"watchdog/{name}",
                     f"Check {name} logs for persistent crash cause. Manual intervention required.",
                     source="watchdog_monitor")
        log_event("restart_loop_detected", "watchdog_monitor", "failure",
                  details={"process": name, "max_restarts": MAX_RESTARTS_PER_WINDOW})
        print(f"[WATCHDOG] ALERT: {name} restart loop — manual intervention needed")
        return False
    if dry_run:
        log_event("process_restart", "watchdog_monitor", "dry_run",
                  details={"process": name})
        print(f"[WATCHDOG] DRY-RUN: Would restart {name}")
        return True
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pid_file = PID_DIR / f"{name}.pid"
        pid_file.write_text(str(proc.pid))
        _restart_history.setdefault(name, []).append(time.time())
        log_event("process_restarted", "watchdog_monitor", "success",
                  details={"process": name, "new_pid": proc.pid})
        print(f"[WATCHDOG] Restarted {name} (PID: {proc.pid})")
        return True
    except Exception as e:
        create_alert(f"{name} restart failed", f"Could not restart {name}: {e}",
                     f"watchdog/{name}", f"Check if {name} script exists and is executable.",
                     source="watchdog_monitor")
        log_event("restart_failed", "watchdog_monitor", "failure",
                  details={"process": name, "error": str(e)[:200]})
        print(f"[WATCHDOG] FAILED to restart {name}: {e}")
        return False


def check_processes(processes, dry_run=False):
    """Check all monitored processes and restart any that are not running."""
    for proc_info in processes:
        name = proc_info["name"]
        pid = read_pid(name)
        if is_running(pid):
            continue
        print(f"[WATCHDOG] {name} not running (PID: {pid})")
        restart_process(proc_info, dry_run)


def main():
    ap = argparse.ArgumentParser(description="Watchdog Monitor – Gold Tier")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--processes", default="", help="JSON list of processes to monitor")
    ap.add_argument("--once", action="store_true", help="Check once and exit")
    args = ap.parse_args()
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"
    processes = json.loads(args.processes) if args.processes else DEFAULT_PROCESSES
    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"Watchdog started ({mode}). Monitoring {len(processes)} processes.")
    log_event("watchdog_started", "watchdog_monitor", "success",
              details={"mode": mode, "process_count": len(processes)})
    # Write own PID
    (PID_DIR / "watchdog_monitor.pid").write_text(str(os.getpid()))

    def cleanup(signum, frame):
        (PID_DIR / "watchdog_monitor.pid").unlink(missing_ok=True)
        print("\nWatchdog stopped.")
        sys.exit(0)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    try:
        while True:
            check_processes(processes, dry_run)
            if args.once:
                break
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        cleanup(None, None)


if __name__ == "__main__":
    main()
