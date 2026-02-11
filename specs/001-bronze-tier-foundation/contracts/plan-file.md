# Contract: Plan File Format

**Version**: 1.0.0
**Produced by**: Claude Code (via `process_tasks_prompt.md`)
**Consumed by**: Human (review and execute steps)
**Location**: `AI_Employee_Vault/Plans/Plan_<original-name>.md`

## Filename Pattern

```
Plan_{original_name_without_extension}.md
```

**Examples**:
- `Plan_test-task.md`
- `Plan_weekly-summary.md`

If a file with the same name already exists, append a timestamp:
```
Plan_{original_name}_{YYYYMMDD_HHMMSS}.md
```

## YAML Frontmatter (required)

```yaml
---
objective: Summarize the user's weekly tasks into a clear overview
status: complete
---
```

| Field | Type | Required | Values | Description |
| ----- | ---- | -------- | ------ | ----------- |
| objective | string | yes | One sentence | Restated task objective |
| status | string | yes | `pending` &#124; `in_progress` &#124; `complete` | Plan state (set to `complete` when written) |

## Body (required)

Must contain a `## Steps` section with a checkbox list of logical next actions.

```markdown
## Steps
- [ ] Step one description
- [ ] Step two description
- [ ] Step three description
```

## Complete Example

```markdown
---
objective: Summarize the user's weekly tasks into a clear overview
status: complete
---

## Steps
- [ ] Gather all task files from the current week
- [ ] Group tasks by category (work, personal, admin)
- [ ] Write a one-paragraph summary for each category
- [ ] Highlight any overdue or high-priority items
- [ ] Save summary to Dashboard.md under Recent Plans
```

## Validation Rules

1. `objective` MUST be present and be a single sentence
2. `status` MUST be set to `complete` when the plan is fully written
3. `## Steps` section MUST exist
4. Steps MUST use Markdown checkbox syntax (`- [ ]`)
5. At least 2 steps MUST be present
6. Steps MUST be concrete and actionable (not vague)
