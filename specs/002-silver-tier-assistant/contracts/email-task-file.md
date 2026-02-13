# Contract: Email Task File

**Entity**: Task File (Email Variant)
**Created by**: `gmail_watcher.py`
**Location**: `AI_Employee_Vault/Needs_Action/`

## Filename Pattern

```
EMAIL_<YYYYMMDD>_<HHMMSS>_<subject_slug>.md
```

- `<YYYYMMDD>_<HHMMSS>` — local time when the task file was created
- `<subject_slug>` — email subject slugified (lowercase, spaces→hyphens,
  max 50 chars, alphanumeric + hyphens only)

**Example**: `EMAIL_20260213_103045_re-meeting-tomorrow.md`

## Frontmatter (YAML)

```yaml
---
type: email_inbound
created: 2026-02-13T10:30:45+05:00
status: pending
priority: normal
source: gmail:18d4a5b3c2e1f
action_required: no
hitl_type: null
from: john@example.com
subject: "Re: Meeting tomorrow"
message_id: 18d4a5b3c2e1f
---
```

### Field Rules

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| type | string | yes | — | MUST be `email_inbound` |
| created | ISO-8601 | yes | — | MUST include timezone offset |
| status | string | yes | `pending` | MUST be `pending` on creation |
| priority | enum | yes | `normal` | `low\|normal\|high\|urgent` |
| source | string | yes | — | MUST match `gmail:<message_id>` |
| action_required | enum | yes | `no` | `yes\|no` (Claude updates) |
| hitl_type | enum | yes | `null` | `email_send\|post_linkedin\|null` |
| from | string | yes | — | Email address, `(unknown)` fallback |
| subject | string | yes | — | Email subject, `(no subject)` fallback |
| message_id | string | yes | — | Gmail message ID |

## Body

Plain text extracted from the email body. If the email is multipart, use
the `text/plain` part. If only `text/html` exists, strip HTML tags to
produce plain text.

```markdown
Hi,

Can we move the meeting to 3 PM? I have a conflict at 2.

Thanks,
John
```

## Validation Checklist

- [ ] Filename matches `EMAIL_<date>_<time>_<slug>.md` pattern
- [ ] All required frontmatter fields present
- [ ] `type` is exactly `email_inbound`
- [ ] `status` is `pending`
- [ ] `source` starts with `gmail:`
- [ ] `from` is non-empty
- [ ] `subject` is non-empty
- [ ] Body contains email text (may be empty for empty emails)
- [ ] No duplicate task file for same `message_id` exists
