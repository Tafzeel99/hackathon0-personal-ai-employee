---
id: 11
title: Update CLAUDE.md Gold Rules
stage: general
date: 2026-02-14
surface: agent
model: claude-opus-4-6
feature: none
branch: 002-silver-tier-assistant
user: tafzeel
command: now update CLAUDE.md
labels: ["claude-md", "gold-tier", "governance", "development-guidelines"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - null
---

## Prompt

now update CLAUDE.md
# Instructions for Claude Code – Gold Tier Autonomous Employee

You are now building the **Gold Tier** of the Personal AI Employee – full autonomy with accounting, multi-social, audits.

## Your Job
- Read /sp.constitution (Gold version) first every time
- Build on Silver: Add Odoo, more social MCPs, full weekly audit, advanced Ralph loop, error recovery
- One major component at a time (Odoo first recommended – it's the biggest lift)
- Expand agent_skills/ aggressively: every new domain gets its own .md
- Ralph Wiggum: Prefer file-move completion check (task in /Done) over promise tag
- Documentation: At end, generate architecture.md (with ASCII diagram) + lessons_learned.md

## Strict Rules (Gold additions)
1. All Odoo actions: draft-only via MCP → HITL for actual post/create
2. Social: Post + summary generation (fetch last N posts → analyze sentiment/trends)
3. Audit: Sunday trigger → full cross-check Odoo + vault → Briefing with numbers + suggestions
4. Error paths: Implement retry_handler.py patterns everywhere; watchdog.py for process monitoring
5. No shortcuts: If X API paid-tier blocked → draft + manual note in plan
6. After each major piece output exactly: GOLD MILESTONE COMPLETE: [description]
7. When entire Gold flow works, output: GOLD TIER AUTONOMOUS EMPLOYEE COMPLETE – READY FOR PLATINUM OR SUBMISSION
8. If Odoo setup/API unclear → ask specific questions

## Recommended Step-by-Step Sequence
1-7 prompts for Odoo setup, MCP flow, social MCPs, Ralph upgrade, weekly audit, watchdog, documentation.

## Response snapshot

Updated CLAUDE.md from Silver to Gold Tier. Key changes: tier header updated to GOLD, constitution reference changed to v3.0.0, scope expanded to include Odoo ERP + 3 social MCPs + weekly audit + error recovery + watchdog + documentation artifacts. Added 17 strict rules (up from 13) covering Odoo HITL, social summary generation, Sunday audit trigger, retry/watchdog patterns, X API fallback, Ralph loop 50-cap with file-move check, 200-line script limit, and documentation generation requirement. Updated scope boundary table, recommended prompts (7 Gold-specific steps), active technologies (odoorpc, facebook-sdk, tweepy, requests-oauthlib), and recent changes log. Added Human as Tool trigger #6 for infrastructure setup questions.

## Outcome

- ✅ Impact: CLAUDE.md now aligned with Gold v3.0.0 constitution — all 10 principles reflected in rules
- 🧪 Tests: null (documentation update)
- 📁 Files: 1 file modified (CLAUDE.md)
- 🔁 Next prompts: Create Gold feature branch, run /sp.specify for Gold feature spec
- 🧠 Reflection: CLAUDE.md serves as the runtime bridge between constitution principles and daily development. Gold additions are significant (17 strict rules) but follow the same pattern.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Verify Gold prompt sequence works by running step 1 (Odoo setup)
