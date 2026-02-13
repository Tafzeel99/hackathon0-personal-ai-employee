---
id: 2
title: Silver Tier Constitution Upgrade
stage: constitution
date: 2026-02-13
surface: agent
model: claude-opus-4-6
feature: none
branch: 001-bronze-tier-foundation
user: tafzeel
command: /sp.constitution
labels: ["constitution", "silver-tier", "hackathon-0", "upgrade"]
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

Project: Personal AI Employee – Silver Tier Functional Assistant
Hackathon 0: Building Autonomous FTEs in 2026

Core principles:
- Local-first & privacy-centric: Obsidian vault remains single source of truth
- Proactive but safe: Watchers detect → Claude reasons → actions only after HITL where needed
- Modularity: All AI logic in Agent Skills (Markdown files)
- Human accountability: Strict folder-based HITL for external/sensitive actions
- Spec-driven & incremental: Build on Bronze; add one capability at a time
- Cost & simplicity: Low API usage; prefer polling/simple scripts over heavy frameworks

Key standards:
- Vault structure extension from Bronze: Add /Pending_Approval, /Approved, /Rejected folders
- Watchers: Minimum two (filesystem + Gmail via Google API OAuth – no pip if possible, use pre-installed or minimal)
- MCP: At least one server (email-mcp for Gmail send/draft via API)
- Agent Skills: Expand to include email_skills.md, approval_skills.md, social_post_skills.md
- Frontmatter enhanced: Add fields like action_required: yes/no, hitl_type: email_send | post_linkedin
- Plan.md format: Must include approval request section if HITL needed
- HITL workflow: Claude creates file in /Pending_Approval → human moves to /Approved → orchestrator/MCP executes
- Logs: Upgrade to simple JSON append in /Logs/YYYY-MM-DD.json (action, timestamp, result)
- Scheduling: Simple cron or Python loop for weekly CEO Briefing generation
- Claude interaction: Use Claude Code CLI with Ralph Wiggum loop (max 20-30 iterations) for persistence on multi-step tasks

Constraints:
- Scope: Silver Tier only – add Gmail watcher + email MCP + basic LinkedIn post draft + HITL + scheduling
- No Odoo, no full social summaries, no WhatsApp Playwright (yet), no cloud/Platinum
- Dependencies: Minimal pip (google-api-python-client, oauth2client if needed; fallback to requests if API simple)
- No direct Claude vault writes: Use orchestrator script to mediate
- Secrets: Use .env for Gmail credentials (gitignored)
- File claim-by-move: Orchestrator moves from /Needs_Action to /In_Progress to prevent duplicates
- No infinite loops: Ralph Wiggum must check TASK_COMPLETE or file in /Done

Success criteria:
- Two Watchers running: Filesystem detects drop → creates task; Gmail detects unread → creates task
- Orchestrator script claims task, calls Claude Code with vault context + Agent Skills
- Claude generates Plan.md + if HITL needed, creates approval file in /Pending_Approval
- Human moves approval file → orchestrator detects → calls MCP to send email/draft LinkedIn post
- Basic LinkedIn post generation: Claude drafts post in Plan.md → MCP (or manual) posts (use API if simple)
- Weekly CEO Briefing: Scheduled task generates Briefing.md with summary of /Done tasks
- End-to-end demo: Email arrives → task → plan → approval → send → log + move to /Done
- All code follows Bronze constraints + new Silver ones
- Zero external actions without approval path
- Output exactly when full Silver ready: SILVER TIER FUNCTIONAL ASSISTANT COMPLETE – READY FOR GOLD UPGRADE

Milestone completion phrase:
SILVER MILESTONE COMPLETE: [short description, e.g., Gmail Watcher + MCP integrated]

## Response snapshot

Upgraded constitution from v1.0.0 (Bronze) to v2.0.0 (Silver). MAJOR version bump due to backward-incompatible governance changes: Bronze constraints replaced with Silver scope expansion. Evolved 5 principles to 6 (added "Cost & Simplicity"), reframed existing principles for Silver context (e.g., "Human Remains in Control" → "Human Accountability" with HITL workflow). Added new sections: HITL Workflow, MCP Integration, Scheduling, Ralph Wiggum Loop, Orchestrator Pattern, Gmail Watcher trigger. Vault structure extended with Pending_Approval/, Approved/, Rejected/ folders. Frontmatter schema extended with action_required and hitl_type fields. Sync Impact Report confirms plan/spec/tasks templates are compatible; README.md and CLAUDE.md flagged for manual update after Silver implementation begins.

## Outcome

- ✅ Impact: Constitution upgraded from Bronze v1.0.0 to Silver v2.0.0; all Silver scope codified
- 🧪 Tests: none (documentation artifact)
- 📁 Files: .specify/memory/constitution.md (upgraded v1.0.0 → v2.0.0)
- 🔁 Next prompts: Update CLAUDE.md for Silver rules, create Silver feature spec with /sp.specify
- 🧠 Reflection: Clean upgrade path; Bronze heritage preserved; all 6 principles testable and declarative

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS (no unresolved placeholders, all sections filled)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
