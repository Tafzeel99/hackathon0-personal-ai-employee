# Odoo Skills — Gold Tier

You are creating and managing Odoo ERP draft invoices and payments.
Follow these rules exactly.

## When to Create an Invoice

Create a draft invoice when the task mentions ANY of:
- Invoice, billing, or charging a client
- Consulting fees, service delivery, or project completion
- Product sale or order fulfillment
- Any request to bill or invoice a party

## When to Create a Payment

Create a draft payment when the task mentions ANY of:
- Payment received from a client
- Recording a deposit or advance
- Settling an outstanding invoice
- Bank transfer or cash receipt

## Required Fields — Invoice

When creating an invoice, you MUST provide:
- **partner_name**: Client/company name (search Odoo partners first)
- **lines**: Array of line items, each with:
  - `name`: Description of service/product
  - `quantity`: Number of units (default: 1)
  - `price_unit`: Price per unit in PKR
- **reference**: Short reference (e.g., "CONSULT-2026-001", project name)

Example data JSON:
```json
{
  "partner_name": "Client X",
  "reference": "CONSULT-2026-001",
  "lines": [
    {"name": "AI Consulting Services - February 2026", "quantity": 1, "price_unit": 50000}
  ]
}
```

## Required Fields — Payment

When creating a payment, you MUST provide:
- **partner_name**: Client/company name
- **amount**: Payment amount in PKR
- **reference**: Reference linking to the invoice or project

## Validation Rules

Before creating any Odoo record:
1. Verify the partner exists in Odoo (use get_partner action)
2. If partner not found, flag for HITL with note: "New partner — requires manual creation"
3. Verify amounts are positive and reasonable
4. If amount exceeds PKR 100,000 — add escalation note: "High-value transaction"
5. Ensure reference field is populated (never leave blank)

## Odoo Field Mappings

| Plan Field | Odoo Model | Odoo Field |
|---|---|---|
| Partner name | res.partner | name |
| Invoice line description | account.move.line | name |
| Line quantity | account.move.line | quantity |
| Line unit price | account.move.line | price_unit |
| Invoice reference | account.move | ref |
| Payment amount | account.payment | amount |

## HITL Routing

- **Draft creation**: Does NOT require HITL (internal operation)
- **Confirm/post invoice**: MUST require HITL (action_type: odoo_confirm)
- **Post payment**: MUST require HITL (action_type: odoo_payment)
- **New partner creation**: MUST require HITL (action_type: odoo_confirm)

## Plan.md Integration

When an Odoo operation is needed, add this section to Plan.md:

```markdown
## Odoo Operation

**Action**: create_invoice | create_payment
**Partner**: [partner name]
**Amount**: PKR [amount]
**Reference**: [reference]
**odoo_data**: {"partner_name": "...", "lines": [...], "reference": "..."}
```

Set in frontmatter:
- `action_required: yes`
- `hitl_type: odoo_confirm` (for invoices) or `odoo_payment` (for payments)
- `domain: erp`

## Error Patterns to Watch For

- **Partner not found**: Log warning, suggest creating partner first
- **Authentication failure**: Credentials may have changed — create alert
- **Connection refused**: Odoo may not be running — retry with backoff
- **Validation error**: Check required fields, amounts, and data types
- **Duplicate reference**: Warn but allow (Odoo handles uniqueness)
