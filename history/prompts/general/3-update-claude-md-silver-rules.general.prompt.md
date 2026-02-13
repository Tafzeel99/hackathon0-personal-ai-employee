---
id: 3
title: Update CLAUDE.md Silver Rules
stage: general
date: 2026-02-13
surface: agent
model: claude-opus-4-6
feature: none
branch: 001-bronze-tier-foundation
user: tafzeel
command: direct
labels: ["claude-md", "silver-tier", "hackathon-0", "configuration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - none
---

## Prompt

Update CLAUDE.md # Instructions for Claude Code – Silver Tier Functional Assistant

You are now upgrading the Personal AI Employee to **Silver Tier** on top of completed Bronze.

## Your Job
- Read spec.constitution.md (Silver version) first in every session
- Build incrementally: One component at a time (e.g., Gmail Watcher → MCP email → HITL → LinkedIn draft → scheduling)
- Strictly follow Silver constraints: No Odoo, no full social summaries, minimal dependencies
- Use Agent Skills: Expand /agent_skills/ with new .md files for each capability
- Ralph Wiggum: Implement basic loop in orchestrator for multi-step reasoning (prompt re-injection until complete)
- HITL: Always check approval_skills.md thresholds; create /Pending_Approval files for external actions

## Strict Rules (Silver additions)
1. Never bypass HITL for email send, post, or any external call
2. Orchestrator must mediate all Claude → vault writes (single writer for Dashboard.md)
3. Use .env for Gmail OAuth creds (setup guide in comments)
4. MCP config: Create simple email_mcp.py or node script (use Gmail API)
5. Scheduling: Use schedule lib (if pip allowed) or simple while loop with time.sleep for demo
6. After each major piece, output exactly:
   SILVER MILESTONE COMPLETE: [description]
7. When entire Silver flow works end-to-end, output:
   SILVER TIER FUNCTIONAL ASSISTANT COMPLETE – READY FOR GOLD UPGRADE
8. If ambiguous (e.g., Gmail API setup), ask clarifying questions

## Recommended Step-by-Step Sequence (copy-paste prompts one by one)

1. "Read spec.constitution.md (Silver). Build on existing Bronze vault. Create new folders: /Pending_Approval, /Approved, /Rejected. Update Dashboard.md to show approval queue section. Create agent_skills/approval_skills.md with HITL thresholds."

2. "Implement Gmail Watcher (gmail_watcher.py): Use Google API (minimal deps), poll for unread important emails every 120s, create Needs_Action/EMAIL_*.md with frontmatter + snippet. Include OAuth setup comments."

3. "Create basic MCP for email: email_mcp.py (Python) that sends/drafts Gmail using credentials from .env. Dry-run mode first. Integrate with orchestrator."

4. "Update orchestrator script: Claim-by-move from Needs_Action → In_Progress → call Claude Code → parse plan for HITL → create Pending_Approval if needed → wait for move to Approved → execute MCP."

5. "Add Ralph Wiggum basic loop to orchestrator: Re-prompt Claude if no TASK_COMPLETE after 20 iterations."

6. "Add simple LinkedIn post skill: agent_skills/social_post_skills.md + Claude drafts post in Plan.md. (For now, output draft; MCP post later if API easy.)"

7. "Implement basic scheduling: Python loop or cron comment to generate Monday CEO Briefing from /Done tasks."

Test end-to-end after each milestone: Drop email simulation or real → approval → send/log.

You may begin with step 1. Confirm scope understood. for silver rules

## Response snapshot

Updated CLAUDE.md from Bronze Tier to Silver Tier rules. Changed title, tier reference (BRONZE → SILVER), scope description, and strict rules (expanded from 8 to 13 rules including HITL enforcement, orchestrator mediation, .env usage, MCP config, scheduling). Added Silver Scope Boundary table. Replaced Bronze recommended prompts with 7-step Silver sequence. Updated Active Technologies to include google-api-python-client, python-dotenv, MCP server. Added HITL-specific invocation trigger to Human as Tool strategy. Preserved all tier-agnostic sections (PHR, ADR, execution contract, default policies).

## Outcome

- ✅ Impact: CLAUDE.md now governs Silver Tier development; all Bronze references replaced
- 🧪 Tests: none (configuration artifact)
- 📁 Files: CLAUDE.md (rewritten for Silver Tier)
- 🔁 Next prompts: Begin Silver step 1 — create vault folders + approval_skills.md
- 🧠 Reflection: Clean upgrade; preserved PHR/ADR/execution sections unchanged; scope boundary table matches constitution v2.0.0

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS (no Bronze-only references remain in active rules)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
