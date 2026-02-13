# Contract: Approval Request File

**Entity**: Approval Request
**Created by**: `orchestrator.py` (after Claude identifies external action)
**Location**: `AI_Employee_Vault/Pending_Approval/`

## Filename Pattern

```
APPROVE_<YYYYMMDD>_<HHMMSS>_<action_slug>.md
```

- `<YYYYMMDD>_<HHMMSS>` — local time when approval request was created
- `<action_slug>` — short description (e.g., `email-reply-john`,
  `linkedin-post-ai-services`)

**Example**: `APPROVE_20260213_110000_email-reply-john.md`

## Frontmatter (YAML)

```yaml
---
action_type: email_send
target: john@example.com
content_summary: "Reply to John confirming 3 PM meeting time"
plan_ref: Plans/Plan_re-meeting-tomorrow.md
task_ref: In_Progress/EMAIL_20260213_103045_re-meeting-tomorrow.md
created: 2026-02-13T11:00:00+05:00
status: pending_approval
---
```

### Field Rules

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| action_type | enum | yes | `email_send\|email_draft\|post_linkedin` |
| target | string | yes | Email address or `linkedin` |
| content_summary | string | yes | One-sentence human-readable summary |
| plan_ref | path | yes | MUST point to existing Plan file |
| task_ref | path | yes | MUST point to task in `In_Progress/` |
| created | ISO-8601 | yes | MUST include timezone |
| status | string | yes | MUST be `pending_approval` on creation |

## Body

The **complete content** that will be sent/posted. The human MUST be able
to read and evaluate the full content before approving.

### Email Body Example

```markdown
## Email to Send

**To**: john@example.com
**Subject**: Re: Meeting tomorrow
**Body**:

Hi John,

3 PM works perfectly. I'll update the calendar invite.

Best regards,
[Your Name]
```

### LinkedIn Post Example

```markdown
## LinkedIn Post Draft

Excited to share how our team is leveraging AI automation to transform
daily business operations. From email triage to task planning, the future
of work is here — and it's local-first. 🚀

Key takeaways from our journey:
• AI can handle 80% of routine email responses
• Human oversight remains critical for external communications
• Start small, iterate fast

What's your experience with AI in business? Drop a comment below.

#AIAutomation #FutureOfWork #Hackathon2026
```

## State Transitions

1. Created in `Pending_Approval/` with `status: pending_approval`
2. Human moves to `Approved/` → orchestrator executes action
3. Human moves to `Rejected/` → orchestrator logs rejection
4. After execution/rejection → moved to `Done/`

## Validation Checklist

- [ ] Filename matches `APPROVE_<date>_<time>_<slug>.md` pattern
- [ ] All required frontmatter fields present
- [ ] `action_type` is one of the defined values
- [ ] `target` is non-empty
- [ ] `plan_ref` points to existing file
- [ ] Body contains complete content preview
- [ ] `status` is `pending_approval`
