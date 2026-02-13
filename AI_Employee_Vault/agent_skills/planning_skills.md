# Planning Skill — Silver Tier

When processing a task:

1. **Objective**: Restate the task in one sentence
2. **Steps**: Create a numbered or checkbox list of logical next actions
3. **Status**: Set to "complete" when plan is written

Format the output exactly as:

```markdown
---
objective: [one sentence restating the task]
status: complete
task_ref: [path to original task file]
action_required: yes | no
hitl_type: email_send | email_draft | post_linkedin | null
---

## Steps
- [ ] Step one
- [ ] Step two
- [ ] Step three
```

Rules:
- The objective MUST be a single, clear sentence
- Steps MUST use Markdown checkbox syntax (`- [ ]`)
- Include at least 2 concrete, actionable steps
- Steps should be specific enough to execute without further clarification
- Set status to "complete" once the plan is fully written

## Silver Extensions

### Approval Required Section
When `action_required: yes`, add this section after Steps:

```markdown
## Approval Required

**Action**: [email_send | email_draft | post_linkedin]
**Target**: [email address or "linkedin"]
**Summary**: [one-sentence description of what will be sent/posted]
```

See `approval_skills.md` for HITL threshold rules.

### LinkedIn Post Draft Section
When the task involves social media or LinkedIn, add:

```markdown
## LinkedIn Post Draft

[Full post text, 100-300 words, with hashtags]
```

Set `action_required: yes` and `hitl_type: post_linkedin` in frontmatter.
See `social_post_skills.md` for drafting guidelines.
