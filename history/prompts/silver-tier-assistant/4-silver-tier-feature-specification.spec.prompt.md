---
id: 4
title: Silver Tier Feature Specification
stage: spec
date: 2026-02-13
surface: agent
model: claude-opus-4-6
feature: silver-tier-assistant
branch: 002-silver-tier-assistant
user: tafzeel
command: /sp.specify
labels: ["spec", "silver-tier", "hackathon-0", "feature-spec"]
links:
  spec: specs/002-silver-tier-assistant/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-silver-tier-assistant/spec.md
  - specs/002-silver-tier-assistant/checklists/requirements.md
tests:
  - none
---

## Prompt

/sp.specify – Silver Tier Specification
Personal AI Employee – Hackathon 0: Building Autonomous FTEs in 2026

## 1. Objective
Transform the Bronze Tier skeleton into a **functional assistant** capable of:
- Detecting real inputs (Gmail + filesystem)
- Reasoning autonomously with Claude Code (creating plans, requesting approvals)
- Executing limited external actions (email send/draft, basic LinkedIn post draft)
- Enforcing human-in-the-loop for sensitive operations
- Producing a basic scheduled CEO Briefing

Silver Tier makes the AI proactive and useful for daily personal/business tasks, while staying local-first and safe.

## 2. Core Principles (non-negotiable – build on Bronze)
- Proactive perception: Watchers push events → no polling by Claude
- Safe autonomy: External actions blocked until human approval via file move
- Single source of truth: Obsidian vault (Markdown only)
- Intelligence encapsulation: Every capability described in agent_skills/*.md
- Traceability & audit: Every action logged (simple JSON append)
- Incremental safety: Dry-run flags in MCP; no irreversible actions without HITL
- Cost awareness: Minimize Claude API calls; prefer short, focused prompts

## 3. In Scope
- Two Watchers: filesystem + Gmail (OAuth + API)
- Orchestrator upgrade: claim-by-move, Ralph Wiggum basic loop, HITL detection
- MCP: email-mcp (send/draft Gmail using Google API)
- HITL workflow: /Pending_Approval → human move → /Approved → execute MCP
- LinkedIn post draft generation in Plan.md
- Scheduling: Monday CEO Briefing from /Done + logs
- Agent Skills: planning, email, approval, social_post
- Logging: /Logs/YYYY-MM-DD.json

## 4. Out of Scope
- WhatsApp, Odoo, full social media, cloud, multi-agent, signed logs, role-based approvals

## 5-8. [Full vault structure, acceptance criteria, demo flow, constraints table provided]

## Response snapshot

Created Silver Tier feature specification at `specs/002-silver-tier-assistant/spec.md` on branch `002-silver-tier-assistant`. The spec contains 5 user stories (P1: Gmail Watcher, P2: Orchestrator + HITL, P3: Email MCP, P4: LinkedIn Drafting, P5: CEO Briefing), 18 functional requirements, 6 key entities, 6 edge cases, 6 assumptions, and 11 measurable success criteria. Quality checklist at `specs/002-silver-tier-assistant/checklists/requirements.md` passes all items — no NEEDS CLARIFICATION markers, all requirements testable, success criteria technology-agnostic.

## Outcome

- ✅ Impact: Complete Silver Tier spec ready for planning phase
- 🧪 Tests: none (specification artifact)
- 📁 Files: spec.md (created), checklists/requirements.md (created)
- 🔁 Next prompts: /sp.plan to create implementation plan, or /sp.clarify to refine
- 🧠 Reflection: User input was comprehensive enough to resolve all ambiguities without NEEDS CLARIFICATION markers; assumptions documented for Gmail setup and LinkedIn approach

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): checklist validation PASS (all items checked)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
