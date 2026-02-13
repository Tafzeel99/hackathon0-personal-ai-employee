# Implementation Plan: Silver Tier Functional Assistant

**Branch**: `002-silver-tier-assistant` | **Date**: 2026-02-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-silver-tier-assistant/spec.md`

## Summary

Transform the Bronze Tier skeleton into a functional assistant by adding a
Gmail watcher (OAuth polling), an orchestrator with claim-by-move and Ralph
Wiggum loop, an email MCP server for Gmail send/draft, folder-based HITL
approval workflow, LinkedIn post drafting via Agent Skills, structured JSON
logging, and a scheduled weekly CEO Briefing generator. All capabilities
build on the existing Bronze vault structure and patterns.

## Technical Context

**Language/Version**: Python 3.8+ (stdlib + minimal pip)
**Primary Dependencies**: google-api-python-client, google-auth-oauthlib,
python-dotenv (all via pip)
**Storage**: Local filesystem — Markdown files in `AI_Employee_Vault/`,
JSONL in `Logs/`
**Testing**: Manual end-to-end demo flow (no pytest framework in Silver scope)
**Target Platform**: Local machine (Windows WSL2 / Linux / macOS)
**Project Type**: Single project — scripts at repository root, vault in
`AI_Employee_Vault/`
**Performance Goals**: Gmail polling every 120s, filesystem polling every 15s,
HITL execution within 2 minutes of approval
**Constraints**: Each script < 150 lines, no heavy frameworks, HITL required
for all external actions, secrets in `.env` only
**Scale/Scope**: Single user, single machine, ~10-50 tasks/week

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Gate | Status |
|---|-----------|------|--------|
| I | Local-First & Privacy-Centric | All state in vault, secrets in `.env` (gitignored), no cloud storage | ✅ PASS |
| II | Proactive but Safe | Watchers auto-detect, HITL gates all external actions, no bypass path | ✅ PASS |
| III | Modularity | Each capability = separate Agent Skill `.md` + separate script, no hardcoded intelligence | ✅ PASS |
| IV | Human Accountability | Folder-based HITL: `Pending_Approval/` → human move → `Approved/`/`Rejected/` | ✅ PASS |
| V | Spec-Driven & Incremental | Builds on Bronze (extend, not replace), one component at a time | ✅ PASS |
| VI | Cost & Simplicity | Polling loops, < 150 lines/script, 3 pip packages only | ✅ PASS |

**Result**: All 6 gates PASS. No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-silver-tier-assistant/
├── plan.md              # This file
├── research.md          # Phase 0: technology decisions
├── data-model.md        # Phase 1: entity schemas
├── quickstart.md        # Phase 1: setup and run guide
├── contracts/           # Phase 1: file format contracts
│   ├── email-task-file.md
│   ├── approval-request-file.md
│   ├── log-entry.md
│   └── briefing-file.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2: /sp.tasks output
```

### Source Code (repository root)

```text
AI_Employee_Vault/
├── Dashboard.md                  # Updated: approval queue + briefing link
├── Company_Handbook.md           # Updated: HITL rules section
├── Business_Goals.md             # Updated: weekly review cadence
├── agent_skills/
│   ├── planning_skills.md        # Bronze (retained)
│   ├── process_tasks_prompt.md   # Bronze (retained)
│   ├── email_skills.md           # NEW: email handling rules
│   ├── approval_skills.md        # NEW: HITL routing thresholds
│   └── social_post_skills.md     # NEW: LinkedIn drafting rules
├── watch_inbox/
├── Needs_Action/
├── In_Progress/
├── Plans/
├── Pending_Approval/             # NEW: HITL requests
├── Approved/                     # NEW: human-approved actions
├── Rejected/                     # NEW: human-rejected actions
├── Done/
├── Inbox/
├── Logs/                         # Upgraded: JSONL format
└── Briefings/                    # NEW: weekly briefings

filesystem_watcher.py             # Bronze (retained as-is)
gmail_watcher.py                  # NEW: Gmail inbox poller
orchestrator.py                   # NEW: task claim + Claude + HITL
email_mcp.py                      # NEW: Gmail send/draft MCP
briefing_generator.py             # NEW: weekly CEO Briefing
log_utils.py                      # NEW: shared JSON logging utility
.env                              # NEW: Gmail OAuth secrets (gitignored)
.env.example                      # NEW: template for .env setup
requirements.txt                  # NEW: pip dependencies
```

**Structure Decision**: Single project at repository root. Scripts are flat
(no `src/` nesting) to match the Bronze pattern (`filesystem_watcher.py` at
root). This keeps the project simple and consistent with the hackathon
"scripts + vault" architecture. The `AI_Employee_Vault/` directory remains
the single data store.

## Complexity Tracking

> No constitution violations detected. Table left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
