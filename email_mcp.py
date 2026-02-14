# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
# Usage: python email_mcp.py --to X --subject Y --body Z [--draft-only] [--dry-run]
"""Email MCP: sends or drafts Gmail messages after HITL approval."""
import argparse, json, os, sys
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

SCOPES = ["https://www.googleapis.com/auth/gmail.send",
           "https://www.googleapis.com/auth/gmail.compose"]


def authenticate(creds_file, token_file):
    """Authenticate with Gmail API via OAuth 2.0 (shared creds with gmail_watcher)."""
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


def build_message(to, subject, body):
    """Build a base64url-encoded RFC 2822 email message."""
    import base64
    from email.mime.text import MIMEText
    msg = MIMEText(body)
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw}


def send_email(service, to, subject, body):
    """Send an email via Gmail API with retry on transient errors."""
    message = build_message(to, subject, body)

    def _send():
        return service.users().messages().send(userId="me", body=message).execute()

    result = retry_call(_send, source="email_mcp", task_ref=f"send:{to}")
    return {"status": "sent", "to": to, "subject": subject, "message_id": result.get("id", "")}


def create_draft(service, to, subject, body):
    """Create a draft in Gmail with retry on transient errors."""
    message = build_message(to, subject, body)

    def _draft():
        return service.users().drafts().create(userId="me", body={"message": message}).execute()

    result = retry_call(_draft, source="email_mcp", task_ref=f"draft:{to}")
    return {"status": "drafted", "to": to, "subject": subject, "draft_id": result.get("id", "")}


def main():
    ap = argparse.ArgumentParser(description="Email MCP – Gold Tier")
    ap.add_argument("--to", required=True, help="Recipient email address")
    ap.add_argument("--subject", required=True, help="Email subject line")
    ap.add_argument("--body", required=True, help="Email body text")
    ap.add_argument("--draft-only", action="store_true", help="Create draft instead of sending")
    ap.add_argument("--dry-run", action="store_true", help="Log but do not call Gmail API")
    args = ap.parse_args()

    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"

    if dry_run:
        result = {"status": "dry_run", "to": args.to, "subject": args.subject}
        log_event("email_dry_run", "email_mcp", "dry_run",
                  details={"to": args.to, "subject": args.subject})
        print(json.dumps(result))
        return

    creds_file = os.environ.get("GMAIL_CREDENTIALS_FILE", "credentials.json")
    token_file = os.environ.get("GMAIL_TOKEN_FILE", "token.json")

    try:
        service = authenticate(creds_file, token_file)
        if args.draft_only:
            result = create_draft(service, args.to, args.subject, args.body)
            log_event("email_drafted", "email_mcp", "success",
                      details={"to": args.to, "subject": args.subject})
        else:
            result = send_email(service, args.to, args.subject, args.body)
            log_event("email_sent", "email_mcp", "success",
                      details={"to": args.to, "subject": args.subject})
        print(json.dumps(result))
    except Exception as e:
        result = {"status": "error", "error": str(e), "to": args.to, "subject": args.subject}
        log_event("email_failed", "email_mcp", "failure",
                  details={"to": args.to, "error": str(e)[:200]})
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
