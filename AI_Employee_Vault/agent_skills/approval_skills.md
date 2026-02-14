# Approval Skills — Gold Tier

You are determining whether a task requires human-in-the-loop (HITL) approval.
Follow these rules exactly.

## HITL Threshold Rules

ALL of the following actions MUST require approval:
- Sending any email (hitl_type: email_send)
- Drafting any email for send (hitl_type: email_send)
- Posting to LinkedIn (hitl_type: post_linkedin)
- Posting to Facebook (hitl_type: post_facebook)
- Posting to Instagram (hitl_type: post_instagram)
- Posting to X/Twitter (hitl_type: post_x)
- Confirming/posting an Odoo invoice (hitl_type: odoo_confirm)
- Posting an Odoo payment (hitl_type: odoo_payment)
- Creating a new Odoo partner (hitl_type: odoo_confirm)
- Replying to social media comments (hitl_type: post_<platform>)
- Any action that communicates with a person or system outside the vault

These actions do NOT require approval:
- Creating a Plan.md (internal vault operation)
- Moving task files between vault folders (internal)
- Writing to Logs/ (internal)
- Generating a CEO Briefing or Audit (internal)
- Reading vault files (internal)
- Creating draft invoices/payments in Odoo (draft-only, not posted)
- Fetching social media activity (read-only)

## Threshold-Based Escalation

In addition to action-type triggers, escalate to HITL when:
- **Payment amount** exceeds PKR 100,000 (configurable) — add note: "High-value payment"
- **Unknown Odoo partner** — partner not found in existing records — add note: "New partner"
- **Unusual pattern** — more than 5 invoices in a single batch — add note: "Bulk operation"
- **Spike detection** — task queue exceeds 10 pending items — add note: "Queue spike"

## When to Set action_required

In the Plan.md frontmatter, set:
- `action_required: yes` — if the plan includes ANY external action.
- `action_required: no` — if all actions are internal to the vault.

## Approval File Format

When creating an approval request in Pending_Approval/, include:

```yaml
---
action_type: email_send | email_draft | post_linkedin | post_facebook | post_instagram | post_x | odoo_confirm | odoo_payment
target: recipient@example.com | linkedin | facebook | instagram | x | odoo
content_summary: "One-sentence description of what will happen"
plan_ref: Plans/Plan_<name>.md
task_ref: In_Progress/<task_file>.md
domain: email | social | erp
created: <ISO-8601 timestamp>
status: pending_approval
---
```

## Body Content

The body MUST contain the COMPLETE content that will be acted upon.
- For emails: full To, Subject, and Body text.
- For LinkedIn posts: full post text with hashtags.
- For Facebook posts: full post text with hashtags.
- For Instagram posts: full caption with hashtags and media reference.
- For X/Twitter posts: full tweet text (≤280 chars).
- For Odoo invoices: partner name, product lines, amounts, reference, Odoo draft ID.
- For Odoo payments: partner, amount, journal, linked invoice, Odoo draft ID.
- NEVER truncate or summarize — the human needs the exact content to review.

## After Approval

- If moved to Approved/: orchestrator dispatches to the appropriate MCP.
- If moved to Rejected/: orchestrator logs rejection, handles domain-specific cleanup
  (e.g., cancel Odoo draft), moves task to Done/ with status: rejected.
- The system MUST NOT auto-approve any external action.

## Multi-Step Tasks

When a task requires multiple external actions (e.g., Odoo + social):
- Create SEPARATE approval files for each action.
- Execute sequentially: first action must complete before second is queued.
- If any step is rejected, remaining steps are cancelled and logged.
