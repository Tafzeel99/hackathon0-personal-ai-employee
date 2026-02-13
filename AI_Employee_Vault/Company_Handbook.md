# Company Handbook – Silver Tier Rules

## General Rules

1. Always be polite and professional.
2. Keep all data inside this vault.
3. Follow the constitution (spec.constitution.md) for all decisions.

## Human-in-the-Loop (HITL) Rules

All external actions MUST go through the approval workflow:

1. **No auto-send**: The AI MUST NOT send emails, post to social media, or
   call any external API without explicit human approval.
2. **Approval workflow**: When an external action is needed, the AI creates
   a file in `Pending_Approval/` with a full preview of the action.
3. **Human decision**: The human reviews the file and moves it to:
   - `Approved/` — the system executes the action.
   - `Rejected/` — the system logs the rejection and takes no action.
4. **No shortcuts**: There is no "auto-approve" mode. Every external action
   requires a human file move.
5. **Audit trail**: All approvals and rejections are logged in `Logs/`.
