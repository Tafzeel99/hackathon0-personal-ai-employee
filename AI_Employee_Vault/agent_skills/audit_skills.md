# Audit Skills — Gold Tier

You are generating the weekly autonomous audit and CEO Briefing.
Follow these rules exactly.

## Audit Trigger

The audit runs:
- **Automatically**: Sunday night (orchestrator schedule check, weekday == 6)
- **Manually**: `python audit_generator.py --generate-audit` or `python orchestrator.py --generate-audit`

## Data Sources

The audit MUST read from three domains:

1. **Odoo Transactions** (via `odoo_mcp.py --action list_invoices/list_payments`):
   - Invoices created, confirmed, paid in the last 7 days
   - Payment records for the period
   - Outstanding amounts

2. **Vault Done/ Tasks** (filesystem scan):
   - All task files in `Done/` with `created` date in the last 7 days
   - Group by domain: email, social, erp, internal/file_drop

3. **Social Summaries** (from `Briefings/Social_Summary_*.md`):
   - Recent social activity summaries
   - Engagement metrics per platform

## Five Mandatory Sections

The audit briefing MUST contain exactly these sections:

### 1. Revenue Summary
- **Total Invoiced**: Sum of all invoice amounts from Odoo (last 7 days)
- **Total Paid**: Sum of all confirmed payment amounts
- **Outstanding**: Total Invoiced - Total Paid
- **Format**: Use PKR currency, include count of invoices/payments
- **Zero case**: "No transactions this period" — still generate valid section

### 2. Completed Tasks by Domain
- Group completed tasks by domain: Email, Social, ERP, File/Internal
- Show count per domain and brief summary of each
- Include completion rate: (completed / total claimed) as percentage

### 3. Bottleneck Analysis
- **Longest duration tasks**: Tasks that took >24 hours from created → Done/
- **Stuck approvals**: Items in Pending_Approval/ older than 48 hours
- **Queue depth**: Current items in Needs_Action/ and In_Progress/
- **Domain health**: Flag any domains with consecutive failures

### 4. Social Activity Summary
- Reference the most recent Social_Summary file
- Aggregate: total posts, total engagement, most active platform
- Highlight any potential leads detected in comments
- If no social activity: "No social posts this period"

### 5. Proactive Suggestions
Generate 3-5 data-driven recommendations based on the data:
- If email volume is high → suggest filters or auto-categorization
- If approval queue is large → suggest mid-week triage session
- If social engagement is low → suggest content strategy adjustment
- If revenue is below target → suggest outreach or follow-ups
- If a domain has failures → suggest checking API credentials

## Output Format

Write to `Briefings/Audit_YYYY-MM-DD.md`:

```markdown
---
type: weekly_audit
period_start: <ISO date>
period_end: <ISO date>
generated: <ISO timestamp>
task_count: <number>
revenue_total: <number>
---

# Weekly Audit — [date range]

## 1. Revenue Summary
[content]

## 2. Completed Tasks
[content]

## 3. Bottleneck Analysis
[content]

## 4. Social Activity Summary
[content]

## 5. Proactive Suggestions
[content]
```

## Validation Rules

Before writing the audit:
- Verify at least the Done/ scan was successful (core data)
- If Odoo is unreachable, note "Odoo data unavailable" but still generate audit
- If social data is empty, note "No social activity data" but still generate audit
- Never fail the audit due to one missing data source — degrade gracefully
