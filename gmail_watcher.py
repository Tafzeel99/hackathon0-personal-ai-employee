# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Gmail watcher: polls inbox for unread emails, creates task files."""
import argparse, base64, os, re, signal, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    sys.exit("Missing deps. Run: pip install -r requirements.txt")
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
from log_utils import log_event
from retry_handler import retry_call

VAULT = Path(__file__).parent / "AI_Employee_Vault"
NEEDS_ACTION = VAULT / "Needs_Action"
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
PKT = timezone(timedelta(hours=5))
PID_FILE = Path(__file__).parent / "gmail_watcher.pid"


def authenticate(creds_file, token_file):
    creds = None
    tp = Path(token_file)
    if tp.exists():
        creds = Credentials.from_authorized_user_file(str(tp), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(creds_file).exists():
                sys.exit(f"Missing {creds_file}. See quickstart.md.")
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
        tp.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def slugify(text, max_len=50):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:max_len]


def extract_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part.get("body", {}):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
    if "body" in payload and "data" in payload["body"]:
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    return ""


def create_task_file(msg_data, service, dry_run):
    hdrs = {h["name"].lower(): h["value"] for h in msg_data["payload"].get("headers", [])}
    sender, subject = hdrs.get("from", "(unknown)"), hdrs.get("subject", "(no subject)")
    msg_id = msg_data["id"]
    body = extract_body(msg_data["payload"]).strip()
    now = datetime.now(PKT)
    fname = f"EMAIL_{now.strftime('%Y%m%d_%H%M%S')}_{slugify(subject)}.md"
    fpath = NEEDS_ACTION / fname
    fpath.write_text(f"""---
type: email_inbound
created: {now.isoformat()}
status: pending
priority: normal
source: "gmail:{msg_id}"
action_required: no
hitl_type: null
domain: email
from: "{sender}"
subject: "{subject}"
message_id: "{msg_id}"
---

{body}
""", encoding="utf-8")
    if not dry_run:
        def _mark_read():
            service.users().messages().modify(
                userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute()
        retry_call(_mark_read, source="gmail_watcher", task_ref=f"Needs_Action/{fname}")
    result = "dry_run" if dry_run else "success"
    log_event("email_detected", "gmail_watcher", result,
              task_ref=f"Needs_Action/{fname}",
              details={"subject": subject, "from": sender})
    print(f"[{now.strftime('%H:%M:%S')}] Created: {fname}")


def poll_once(service, seen_ids, dry_run):
    try:
        def _list():
            return service.users().messages().list(
                userId="me", q="is:unread", maxResults=10).execute()
        result = retry_call(_list, source="gmail_watcher")
    except Exception as e:
        log_event("error", "gmail_watcher", "failure",
                  details={"error": str(e)[:200]})
        print(f"[ERROR] Gmail API: {e}")
        return
    messages = result.get("messages", [])
    if not messages:
        return
    for msg_meta in messages:
        mid = msg_meta["id"]
        if mid in seen_ids:
            continue
        seen_ids.add(mid)
        try:
            def _get(m=mid):
                return service.users().messages().get(
                    userId="me", id=m, format="full").execute()
            msg = retry_call(_get, source="gmail_watcher")
            create_task_file(msg, service, dry_run)
        except Exception as e:
            log_event("error", "gmail_watcher", "failure",
                      details={"message_id": mid, "error": str(e)[:200]})
            print(f"[ERROR] Message {mid}: {e}")


def cleanup(signum=None, frame=None):
    PID_FILE.unlink(missing_ok=True)
    print("\nGmail watcher stopped.")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Gmail Watcher – Gold Tier")
    parser.add_argument("--auth-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"
    creds_file = os.environ.get("GMAIL_CREDENTIALS_FILE", "credentials.json")
    token_file = os.environ.get("GMAIL_TOKEN_FILE", "token.json")
    interval = int(os.environ.get("GMAIL_POLL_INTERVAL", "120"))
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
    service = authenticate(creds_file, token_file)
    print(f"Gmail authenticated. Token: {token_file}")
    if args.auth_only:
        return
    # PID file management
    PID_FILE.write_text(str(os.getpid()))
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"Gmail watcher started ({mode}). Polling every {interval}s.")
    log_event("watcher_started", "gmail_watcher",
              "dry_run" if dry_run else "success", details=f"Interval: {interval}s")
    seen_ids = set()
    try:
        while True:
            poll_once(service, seen_ids, dry_run)
            time.sleep(interval)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
