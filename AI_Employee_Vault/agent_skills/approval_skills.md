# Approval Skills — Silver Tier

You are determining whether a task requires human-in-the-loop (HITL) approval.
Follow these rules exactly.

## HITL Threshold Rules

ALL of the following actions MUST require approval:
- Sending any email (hitl_type: email_send)
- Drafting any email for send (hitl_type: email_send)
- Posting to LinkedIn (hitl_type: post_linkedin)
- Any action that communicates with a person or system outside the vault

These actions do NOT require approval:
- Creating a Plan.md (internal vault operation)
- Moving task files between vault folders (internal)
- Writing to Logs/ (internal)
- Generating a CEO Briefing (internal)
- Reading vault files (internal)

## When to Set action_required

In the Plan.md frontmatter, set:
- `action_required: yes` — if the plan includes ANY external action.
- `action_required: no` — if all actions are internal to the vault.

## Approval File Format

When creating an approval request in Pending_Approval/, include:

```yaml
---
action_type: email_send | email_draft | post_linkedin
target: recipient@example.com | linkedin
content_summary: "One-sentence description of what will happen"
plan_ref: Plans/Plan_<name>.md
task_ref: In_Progress/<task_file>.md
created: <ISO-8601 timestamp>
status: pending_approval
---
```

## Body Content

The body MUST contain the COMPLETE content that will be sent or posted.
- For emails: full To, Subject, and Body text.
- For LinkedIn posts: full post text with hashtags.
- NEVER truncate or summarize — the human needs the exact content to review.

## After Approval

- If moved to Approved/: orchestrator dispatches to the appropriate MCP.
- If moved to Rejected/: orchestrator logs rejection, moves task to Done/
  with status: rejected.
- The system MUST NOT auto-approve any external action.
