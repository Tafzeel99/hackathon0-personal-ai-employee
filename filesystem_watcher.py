# Bronze Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
#
# Filesystem watcher that polls watch_inbox/ for new .txt and .md files
# and creates structured task files in Needs_Action/ with YAML frontmatter.
# Uses only Python stdlib + pathlib. No external dependencies.

import time
from pathlib import Path
from datetime import datetime, timezone, timedelta


# Vault paths (relative to script location)
SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = SCRIPT_DIR / "AI_Employee_Vault"
WATCH_DIR = VAULT_ROOT / "watch_inbox"
NEEDS_ACTION_DIR = VAULT_ROOT / "Needs_Action"

# Configuration
POLL_INTERVAL = 15  # seconds
ALLOWED_EXTENSIONS = {".txt", ".md"}


def log(message: str) -> None:
    """Print a timestamped log message to console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_local_timezone() -> timezone:
    """Return the local timezone offset."""
    offset = timedelta(seconds=-time.timezone if time.daylight == 0 else -time.altzone)
    return timezone(offset)


def create_task_file(source_path: Path) -> None:
    """Read a source file from watch_inbox/ and create a task file in Needs_Action/.

    The task file includes YAML frontmatter with all 6 required fields
    and the original file content as body.
    """
    now = datetime.now(tz=get_local_timezone())
    timestamp_filename = now.strftime("%Y%m%d_%H%M%S")
    timestamp_iso = now.isoformat()

    # Build task filename: TASK_<name-without-ext>_<YYYYMMDD_HHMMSS>.md
    stem = source_path.stem
    task_filename = f"TASK_{stem}_{timestamp_filename}.md"
    task_path = NEEDS_ACTION_DIR / task_filename

    # Read original file content
    content = source_path.read_text(encoding="utf-8")

    # Build YAML frontmatter per contracts/task-file.md
    frontmatter = (
        "---\n"
        "type: file_drop\n"
        f"created: {timestamp_iso}\n"
        "status: pending\n"
        "priority: medium\n"
        f"source: watch_inbox/{source_path.name}\n"
        f"original_file: {source_path.name}\n"
        "---\n"
    )

    # Write task file
    task_path.write_text(frontmatter + "\n" + content, encoding="utf-8")
    log(f"Created task: Needs_Action/{task_filename}")


def scan_inbox(processed_files: set) -> None:
    """Scan watch_inbox/ for new .txt and .md files.

    Filters by allowed extensions, skips already-processed files,
    and creates task files for new ones.
    """
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


def main() -> None:
    """Entry point: validate directories and start polling loop."""
    # Startup validation
    if not WATCH_DIR.is_dir():
        print(f"ERROR: watch_inbox/ not found at {WATCH_DIR}")
        print("Run vault setup first to create AI_Employee_Vault/ structure.")
        return

    if not NEEDS_ACTION_DIR.is_dir():
        print(f"ERROR: Needs_Action/ not found at {NEEDS_ACTION_DIR}")
        print("Run vault setup first to create AI_Employee_Vault/ structure.")
        return

    log(f"Watcher started. Monitoring {WATCH_DIR}")
    log(f"Polling every {POLL_INTERVAL} seconds for .txt and .md files...")

    processed_files: set = set()

    try:
        while True:
            scan_inbox(processed_files)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        log("Watcher stopped by user (Ctrl+C).")


if __name__ == "__main__":
    main()
