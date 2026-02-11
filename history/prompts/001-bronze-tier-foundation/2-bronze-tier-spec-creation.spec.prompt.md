---
id: 2
title: Bronze Tier Spec Creation
stage: spec
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 001-bronze-tier-foundation
branch: 001-bronze-tier-foundation
user: tafzeel
command: /sp.specify
labels: ["bronze-tier", "specification", "vault-structure", "file-watcher"]
links:
  spec: specs/001-bronze-tier-foundation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-bronze-tier-foundation/spec.md
  - specs/001-bronze-tier-foundation/checklists/requirements.md
tests:
  - Spec quality checklist validated (all items pass)
---

## Prompt

you are working on this and terminal got terminated!
# sp.specify – Bronze Tier Specification
Personal AI Employee – Hackathon 0: Building Autonomous FTEs in 2026

## 1. Objective
Deliver the absolute minimal working foundation of a local-first AI employee that:
- Uses Obsidian vault as memory & dashboard
- Has one simple trigger mechanism (file drop → watcher → task file)
- Allows Claude Code to read tasks and write structured plans inside the vault
- Demonstrates end-to-end flow without any external dependencies

This is Bronze Tier only — no APIs, no external actions, no approvals, no loops beyond basic prompting.

## 2. Core Principles (non-negotiable)
- Everything stays inside one folder: AI_Employee_Vault/
- No network, no pip installs, no credentials, no .env in Bronze
- Intelligence lives only in Markdown Agent Skills files
- Human controls execution: drop file manually → run Claude prompt manually
- Traceability: every task file must have clear origin and frontmatter
- Simplicity first: prefer polling watcher over event-driven libraries

## 3. In Scope (must be delivered)
- Obsidian vault folder structure creation
- Three core Markdown files with minimal content
- One Agent Skill file defining plan format
- Simple Python filesystem watcher (polling loop acceptable)
- End-to-end test: drop → detect → task file → Claude prompt → Plan.md → move to Done/

## 4. Out of Scope (explicitly excluded in Bronze)
- Any API watchers (Gmail, WhatsApp, social)
- MCP servers or external action execution
- Human-in-the-loop approval folders
- Ralph Wiggum persistence loop
- Scheduling, PM2, cron, daemons
- Odoo, accounting, social posting, CEO briefing
- JSON logs (use simple .md logs if needed)
- Error recovery beyond basic print/logging

## 5. Required Artifacts & Exact Structure

AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── agent_skills/
│   └── planning_skills.md
├── watch_inbox/
├── Needs_Action/
├── In_Progress/
├── Plans/
├── Done/
└── Logs/

## 6. Acceptance Criteria (must all pass for Bronze complete)

1. Vault folder structure exists exactly as above
2. All four Markdown files exist with at least the minimal content shown
3. filesystem_watcher.py exists and runs without errors
4. Watcher detects new .txt or .md file in watch_inbox/
5. Watcher creates corresponding file in Needs_Action/ with frontmatter
6. Manual Claude Code prompt processes Needs_Action/ file
7. No external dependencies or installs required to run watcher
8. Watcher uses only stdlib + pathlib (polling loop preferred)
9. End-to-end demo takes < 2 minutes from file drop to Plan.md appearance

## 7. Success Verification Steps
1. Create watch_inbox/test-task.txt with content: "Summarize my weekly tasks"
2. Run watcher (python filesystem_watcher.py)
3. Confirm Needs_Action/TASK_test-task_*.md appears
4. Run Claude Code prompt to process folder
5. Confirm Plans/ contains new .md file with correct format
6. Move task file to Done/ manually
7. Output: BRONZE TIER FOUNDATION COMPLETE – READY FOR SILVER UPGRADE

## 8. Constraints Table

| Aspect              | Allowed in Bronze                  | Forbidden in Bronze                     |
|---------------------|-------------------------------------|------------------------------------------|
| Dependencies        | stdlib + pathlib                   | watchdog, requests, google-api, etc.     |
| Execution           | Manual prompt + watcher script     | Automatic orchestration, scheduling      |
| Claude interaction  | Manual claude command              | API calls, persistent loop               |
| File movement       | Human or simple script             | Watcher moves files                      |
| Logs                | Optional simple .md                | JSON, append-only audit trail            |

## Response snapshot

Created the Bronze Tier Foundation specification at `specs/001-bronze-tier-foundation/spec.md` with:
- 4 user stories (P1-P4): Vault Setup, File Drop Detection, Task Processing/Plan Generation, End-to-End Demo
- 15 functional requirements (FR-001 through FR-015)
- 6 edge cases covering empty files, duplicates, non-target file types, missing dirs
- 9 measurable success criteria (SC-001 through SC-009)
- Scope boundary, assumptions, and constraints tables
- Quality checklist created and all items passed validation
- Zero [NEEDS CLARIFICATION] markers — user input was comprehensive

## Outcome

- Impact: Spec created; feature ready for planning phase
- Tests: Quality checklist passed (all items green)
- Files: spec.md, checklists/requirements.md
- Next prompts: `/sp.plan` to generate architecture plan, or `/sp.clarify` if refinement needed
- Reflection: User provided exceptionally detailed input including exact folder structures, content templates, constraints, and acceptance criteria. No clarification questions needed.

## Evaluation notes (flywheel)

- Failure modes observed: Terminal terminated during previous attempt; recovered by checking existing branch/file state
- Graders run and results (PASS/FAIL): Spec quality checklist PASS (all items)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.plan for architecture design
