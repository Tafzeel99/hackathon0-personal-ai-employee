# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
#
# Filesystem watcher that polls watch_inbox/ for new .txt and .md files
# and creates structured task files in Needs_Action/ with YAML frontmatter.

import os
import signal
import sys
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = SCRIPT_DIR / "AI_Employee_Vault"
WATCH_DIR = VAULT_ROOT / "watch_inbox"
NEEDS_ACTION_DIR = VAULT_ROOT / "Needs_Action"
PID_FILE = SCRIPT_DIR / "filesystem_watcher.pid"

POLL_INTERVAL = 15
ALLOWED_EXTENSIONS = {".txt", ".md"}


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_local_timezone() -> timezone:
    offset = timedelta(seconds=-time.timezone if time.daylight == 0 else -time.altzone)
    return timezone(offset)


def create_task_file(source_path: Path) -> None:
    now = datetime.now(tz=get_local_timezone())
    timestamp_filename = now.strftime("%Y%m%d_%H%M%S")
    timestamp_iso = now.isoformat()
    stem = source_path.stem
    task_filename = f"TASK_{stem}_{timestamp_filename}.md"
    task_path = NEEDS_ACTION_DIR / task_filename
    content = source_path.read_text(encoding="utf-8")
    frontmatter = (
        "---\n"
        "type: file_drop\n"
        f"created: {timestamp_iso}\n"
        "status: pending\n"
        "priority: medium\n"
        f"source: watch_inbox/{source_path.name}\n"
        f"original_file: {source_path.name}\n"
        "domain: internal\n"
        "---\n"
    )
    task_path.write_text(frontmatter + "\n" + content, encoding="utf-8")
    log(f"Created task: Needs_Action/{task_filename}")


def scan_inbox(processed_files: set) -> None:
    for item in WATCH_DIR.iterdir():
        if not item.is_file():
            continue
        if item.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        if item.name in processed_files:
            continue
        log(f"New file detected: {item.name}")
        create_task_file(item)
        processed_files.add(item.name)


def cleanup(signum=None, frame=None):
    PID_FILE.unlink(missing_ok=True)
    log("Watcher stopped.")
    sys.exit(0)


def main() -> None:
    if not WATCH_DIR.is_dir():
        print(f"ERROR: watch_inbox/ not found at {WATCH_DIR}")
        return
    if not NEEDS_ACTION_DIR.is_dir():
        print(f"ERROR: Needs_Action/ not found at {NEEDS_ACTION_DIR}")
        return

    # PID file management
    PID_FILE.write_text(str(os.getpid()))
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    log(f"Watcher started. Monitoring {WATCH_DIR}")
    log(f"Polling every {POLL_INTERVAL} seconds for .txt and .md files...")

    processed_files: set = set()
    try:
        while True:
            scan_inbox(processed_files)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
