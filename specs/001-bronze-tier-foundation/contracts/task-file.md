# Contract: Task File Format

**Version**: 1.0.0
**Produced by**: `filesystem_watcher.py`
**Consumed by**: Claude Code (via `process_tasks_prompt.md`)
**Location**: `AI_Employee_Vault/Needs_Action/TASK_<name>_<timestamp>.md`

## Filename Pattern

```
TASK_{original_name_without_extension}_{YYYYMMDD_HHMMSS}.md
```

**Examples**:
- `TASK_test-task_20260211_040700.md`
- `TASK_weekly-summary_20260211_150000.md`

## YAML Frontmatter (required)

```yaml
---
type: file_drop
created: 2026-02-11T04:07:00+05:00
status: pending
priority: medium
source: watch_inbox/test-task.txt
original_file: test-task.txt
---
```

| Field | Type | Required | Values | Description |
| ----- | ---- | -------- | ------ | ----------- |
| type | string | yes | `file_drop` | Trigger mechanism |
| created | string | yes | ISO-8601 with timezone | When task file was created |
| status | string | yes | `pending` | Always `pending` on creation |
| priority | string | yes | `medium` | Default priority for file drops |
| source | string | yes | Relative path | Path to original file from vault root |
| original_file | string | yes | Filename | Original filename with extension |

## Body (required)

The full text content of the original dropped file, copied verbatim. May be empty if the source file was empty.

## Complete Example

```markdown
---
type: file_drop
created: 2026-02-11T04:07:00+05:00
status: pending
priority: medium
source: watch_inbox/test-task.txt
original_file: test-task.txt
---

Summarize my weekly tasks
```

## Validation Rules

1. All six frontmatter fields MUST be present
2. `created` MUST be valid ISO-8601
3. `status` MUST be `pending` on creation
4. `source` MUST start with `watch_inbox/`
5. `original_file` MUST match the actual filename
6. Body MUST be an exact copy of the source file content
