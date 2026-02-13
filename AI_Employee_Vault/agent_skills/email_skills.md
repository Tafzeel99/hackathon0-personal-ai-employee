# Email Skills — Silver Tier

You are processing an email task file (type: email_inbound) from the vault.
Follow these rules exactly.

## Email Analysis

1. Read the full email body and sender information from the task file.
2. Determine the email intent:
   - **Reply needed**: Sender asks a question, requests a meeting, or expects a response.
   - **Forward needed**: Email should be routed to someone else.
   - **Archive only**: Newsletter, notification, or FYI — no action required.
3. Set `action_required` in the Plan frontmatter:
   - `yes` if reply or forward is needed.
   - `no` if archive only.

## Reply Drafting Rules

When drafting a reply:
- Be professional and concise.
- Mirror the sender's tone (formal if they are formal, friendly if casual).
- Address the sender's question or request directly.
- Include a clear next step or call-to-action.
- Sign off with the user's name (use "[Your Name]" as placeholder).
- Keep replies under 150 words unless the topic requires detail.

## Task File Extraction

When the Gmail watcher creates a task file, it extracts:
- `from`: Sender email address.
- `subject`: Email subject line (use "(no subject)" if empty).
- `message_id`: Gmail message ID for deduplication.
- `body`: Plain text of the email (prefer text/plain, strip HTML if needed).

## HITL Routing

- ALL email sends MUST go through Pending_Approval.
- Set `hitl_type: email_send` in the Plan frontmatter when a reply is drafted.
- The approval file MUST contain the complete email body so the human can
  review before sending.
- NEVER send an email without human approval.
