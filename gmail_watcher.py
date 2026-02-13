# Silver Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Gmail watcher: polls inbox for unread emails, creates task files."""
import argparse, base64, os, re, sys, time
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

VAULT = Path(__file__).parent / "AI_Employee_Vault"
NEEDS_ACTION = VAULT / "Needs_Action"
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
PKT = timezone(timedelta(hours=5))

def authenticate(creds_file, token_file):
    """Authenticate with Gmail API via OAuth 2.0."""
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
    """Extract plain text body from Gmail message payload."""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part.get("body", {}):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
    if "body" in payload and "data" in payload["body"]:
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    return ""


def create_task_file(msg_data, service, dry_run):
    """Create EMAIL_*.md task file from Gmail message."""
    hdrs = {h["name"].lower(): h["value"] for h in msg_data["payload"].get("headers", [])}
    sender = hdrs.get("from", "(unknown)")
    subject = hdrs.get("subject", "(no subject)")
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
from: "{sender}"
subject: "{subject}"
message_id: "{msg_id}"
---

{body}
""", encoding="utf-8")
    if not dry_run:
        service.users().messages().modify(
            userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute()
    result = "dry_run" if dry_run else "success"
    log_event("email_detected", "gmail_watcher", result,
              task_ref=f"Needs_Action/{fname}",
              details=f"Subject: {subject}, From: {sender}")
    print(f"[{now.strftime('%H:%M:%S')}] Created: {fname}")


def poll_once(service, seen_ids, dry_run):
    """Poll Gmail for unread messages, create task files for new ones."""
    try:
        result = service.users().messages().list(
            userId="me", q="is:unread", maxResults=10).execute()
    except Exception as e:
        log_event("error", "gmail_watcher", "failure", details=f"Gmail API: {e}")
        print(f"[ERROR] Gmail API: {e}")
        return
    messages = result.get("messages", [])
    if not messages:
        log_event("watcher_poll", "gmail_watcher", "skipped",
                  details="No new unread messages")
        return
    for msg_meta in messages:
        mid = msg_meta["id"]
        if mid in seen_ids:
            continue
        seen_ids.add(mid)
        try:
            msg = service.users().messages().get(
                userId="me", id=mid, format="full").execute()
            create_task_file(msg, service, dry_run)
        except Exception as e:
            log_event("error", "gmail_watcher", "failure",
                      details=f"Message {mid}: {e}")
            print(f"[ERROR] Message {mid}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Gmail Watcher – Silver Tier")
    parser.add_argument("--auth-only", action="store_true", help="Authenticate and exit")
    parser.add_argument("--dry-run", action="store_true", help="No email marking")
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
        print("\nGmail watcher stopped.")


if __name__ == "__main__":
    main()
