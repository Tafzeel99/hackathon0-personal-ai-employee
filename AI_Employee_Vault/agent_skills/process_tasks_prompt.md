# Process Tasks Prompt – Bronze Tier

Use this prompt with Claude Code to process pending tasks from Needs_Action/ into plans.

## Instructions

1. List all `.md` files in `AI_Employee_Vault/Needs_Action/`.
2. For each file, read the YAML frontmatter. Only process files with `status: pending`.
3. For each pending task:
   a. Read the body content (everything after the frontmatter `---` block).
   b. Read `AI_Employee_Vault/agent_skills/planning_skills.md` for the output format.
   c. Create a plan file in `AI_Employee_Vault/Plans/` following this naming:
      - Extract the original name from the task filename: `TASK_<name>_<timestamp>.md` → use `<name>`
      - Output filename: `Plan_<name>.md`
      - If `Plan_<name>.md` already exists, append a timestamp: `Plan_<name>_<YYYYMMDD_HHMMSS>.md`
   d. The plan file MUST contain:
      - YAML frontmatter with `objective` (one sentence restating the task) and `status: complete`
      - A `## Steps` section with a checkbox list of at least 2 concrete, actionable steps
4. After creating all plans, list the files created.

## Example

Given `Needs_Action/TASK_test-task_20260211_040700.md` with body "Summarize my weekly tasks", create:

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

## Copy-Paste Prompt

```
Read all .md files in AI_Employee_Vault/Needs_Action/ that have status: pending in their frontmatter. For each one, read AI_Employee_Vault/agent_skills/planning_skills.md for the required output format. Then create a Plan file in AI_Employee_Vault/Plans/ named Plan_<original-task-name>.md with YAML frontmatter (objective as one sentence, status: complete) and a ## Steps section with checkbox items. Each step must be concrete and actionable.
```
