---
id: 1
title: Bronze Tier Constitution Creation
stage: constitution
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: tafzeel
command: /sp.constitution
labels: ["constitution", "bronze-tier", "hackathon-0", "setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Project: Personal AI Employee – Bronze Tier Foundation
Hackathon 0: Building Autonomous FTEs in 2026

Core principles:
- Local-first architecture: everything lives inside one Obsidian vault folder
- Minimal viable foundation: only what is explicitly required for Bronze Tier
- Transparency & auditability: every generated file must be traceable to a trigger
- Human remains in control: no external actions, no automatic execution in Bronze
- Spec-driven development: Claude Code generates code & content strictly from this constitution and referenced specs

Key standards:
- Vault structure must match exactly the folders and filenames defined in section 4
- All Claude-generated intelligence must live in agent_skills/*.md files (Agent Skills pattern)
- Frontmatter on every Needs_Action file: type, created, status, priority
- Plan.md files must contain: Objective, Steps (checkbox list), Status
- No external dependencies: no pip installs, no APIs, no network calls
- Code simplicity: watcher < 150 lines, polling preferred over watchdog
- Documentation: every generated Python file starts with comment:
  # Bronze Tier – Hackathon 0 – Personal AI Employee
  # Generated following spec.constitution.md

Constraints:
- Scope: Bronze Tier only (no Gmail, WhatsApp, MCP, approvals, Ralph loop, scheduling, Odoo, social)
- Folder watched: only watch_inbox/ (simple drop folder)
- Trigger mechanism: filesystem watcher creates task in Needs_Action/
- Claude interaction: manual prompt to process Needs_Action/ → create Plans/ → move to Done/
- File movement: watcher never moves files; Claude (or human) moves to Done/
- No secrets, no .env, no credentials in Bronze
- Output files: .md only (no json, no databases)

Success criteria:
- Vault folder structure exists and is opened in Obsidian
- Dashboard.md, Company_Handbook.md, Business_Goals.md exist with minimal content
- agent_skills/planning_skills.md exists and defines Plan.md format
- filesystem_watcher.py runs and detects new files in watch_inbox/
- Dropping test-task.txt in watch_inbox/ → corresponding Needs_Action/TASK_*.md appears with frontmatter
- Running Claude Code with prompt → reads Needs_Action/, creates Plan_*.md in Plans/, moves original task to Done/
- End-to-end demo possible without errors or external dependencies
- All generated code follows Bronze constraints (no installs, no network, simple polling)
- Zero deviation from defined folder names and frontmatter schema

Milestone completion phrase (must be output exactly when achieved):
BRONZE MILESTONE COMPLETE: [short description of completed piece]

When the full Bronze Tier is demonstrably working end-to-end, output:
BRONZE TIER FOUNDATION COMPLETE – READY FOR SILVER UPGRADE

## Response snapshot

Created the Bronze Tier constitution (v1.0.0) at `.specify/memory/constitution.md`. Filled all template placeholders with 5 core principles (Local-First Architecture, Minimal Viable Foundation, Transparency & Auditability, Human Remains in Control, Spec-Driven Development), key standards (vault structure, Agent Skills pattern, frontmatter schema, Plan.md format, code standards), Bronze Tier constraints (scope boundary table, trigger mechanism, success criteria checklist), governance rules, and milestone protocol. Sync Impact Report confirms all dependent templates are compatible with no updates needed. Version 1.0.0 ratified 2026-02-11.

## Outcome

- Impact: Foundation constitution established for entire Bronze Tier development
- Tests: none (documentation artifact)
- Files: .specify/memory/constitution.md (created v1.0.0)
- Next prompts: Create vault folder structure and initial content files per constitution
- Reflection: Clean first constitution; all user-supplied principles mapped 1:1

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS (no unresolved placeholders)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
