# Contract: Briefing File

**Entity**: CEO Briefing
**Created by**: `briefing_generator.py` (or orchestrator with
`--generate-briefing` flag)
**Location**: `AI_Employee_Vault/Briefings/`

## Filename Pattern

```
Monday_YYYY-MM-DD.md
```

- `YYYY-MM-DD` is the date the briefing was generated (typically a Monday)

**Example**: `Monday_2026-02-13.md`

## Frontmatter (YAML)

```yaml
---
type: ceo_briefing
period_start: 2026-02-06
period_end: 2026-02-13
generated: 2026-02-13T08:00:00+05:00
task_count: 12
---
```

### Field Rules

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| type | string | yes | MUST be `ceo_briefing` |
| period_start | ISO-8601 date | yes | MUST be 7 days before period_end |
| period_end | ISO-8601 date | yes | MUST be generation date |
| generated | ISO-8601 | yes | MUST include timezone |
| task_count | integer | yes | Count of completed tasks in period |

## Body Sections

### Section 1: Completed Tasks Summary

Group tasks by type (`file_drop`, `email_inbound`, `scheduled`). For each
task, show a one-line summary with date and outcome.

```markdown
## Completed Tasks (12)

### Email Tasks (7)
- 2026-02-07: Replied to John about Q1 meeting ✅
- 2026-02-08: Drafted response to supplier inquiry ✅
- ...

### File Drop Tasks (4)
- 2026-02-09: Created plan for weekly report ✅
- ...

### Scheduled Tasks (1)
- 2026-02-06: Generated previous week's briefing ✅
```

### Section 2: Pending Items

List tasks still in `Needs_Action/` or `In_Progress/` with age.

```markdown
## Pending Items (3)

- ⏳ EMAIL: Invoice from vendor (2 days old, in Needs_Action)
- ⏳ TASK: Update company handbook (1 day old, in In_Progress)
- ⏳ APPROVE: LinkedIn post about AI services (in Pending_Approval)
```

### Section 3: Proactive Suggestion

One actionable recommendation based on patterns observed.

```markdown
## Proactive Suggestion

📌 You received 7 email tasks this week but only 4 required responses.
Consider creating an email filter to auto-archive newsletters and
notifications, reducing your task queue by ~40%.
```

## Validation Checklist

- [ ] Filename matches `Monday_YYYY-MM-DD.md` pattern
- [ ] All required frontmatter fields present
- [ ] `type` is `ceo_briefing`
- [ ] `period_end` minus `period_start` is 7 days
- [ ] `task_count` matches actual count of Done tasks in period
- [ ] Body has all 3 sections (Completed, Pending, Suggestion)
- [ ] No tasks missing from the summary
