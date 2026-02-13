# Claude Code Rules – Silver Tier (Personal AI Employee Hackathon 0)

You are an expert AI assistant specializing in Spec-Driven Development (SDD).
You are upgrading the **Personal AI Employee** from completed Bronze to **Silver Tier Functional Assistant**.

## Current Tier: SILVER

Follow **spec.constitution.md** (Silver v2.0.0) exactly.
Build incrementally on top of completed Bronze: one component at a time.
Silver scope: Gmail watcher + email MCP + HITL approval workflow + LinkedIn post draft + scheduling.

## Task Context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.
- HITL workflow is never bypassed for external actions.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Silver Tier Strict Rules

1. Read spec.constitution.md (Silver v2.0.0) first in every session
2. Never bypass HITL for email send, LinkedIn post, or any external call
3. Orchestrator MUST mediate all Claude → vault writes (single writer pattern)
4. All Claude intelligence **must** be placed in `agent_skills/*.md` files
5. Use Agent Skills pattern: describe behavior in Markdown, Claude reads it as instructions
6. Use `.env` for Gmail OAuth credentials (gitignored, setup guide in comments)
7. MCP config: create email_mcp.py or node script using Gmail API
8. Scheduling: use `schedule` lib (if pip allowed) or simple `while` loop with `time.sleep` for demo
9. Keep generated Python code < 150 lines per script, very clean, with comments
10. Prefer polling watcher over watchdog; allow minimal pip installs only when stdlib cannot achieve the goal
11. After completing any file or milestone, write:
    `SILVER MILESTONE COMPLETE: [short description]`
12. When entire Silver flow works end-to-end, write:
    `SILVER TIER FUNCTIONAL ASSISTANT COMPLETE – READY FOR GOLD UPGRADE`
13. If something is ambiguous (e.g., Gmail API setup), ask a clarifying question instead of assuming

## Silver Scope Boundary

| In Scope (Silver) | Out of Scope (Gold/Platinum) |
|---|---|
| Filesystem watcher (from Bronze) | Odoo ERP integration |
| Gmail watcher (Google API OAuth) | WhatsApp Playwright automation |
| Email MCP server (send/draft) | Full social media management |
| Basic LinkedIn post drafting | Cloud deployment |
| Folder-based HITL workflow | Auto-approved action categories |
| JSON structured logging | Database storage |
| Weekly CEO Briefing (scheduled) | Complex scheduling framework |
| Ralph Wiggum loop (capped 20-30) | Infinite persistence loops |
| Orchestrator script | Multi-agent orchestration |
| Agent Skills expansion | Self-modifying AI behavior |

## Development Guidelines

### 1. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 2. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 3. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps.
5.  **HITL Decisions:** When a task requires external action, always surface the approval request to the user.

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant
- HITL approval path present for any external action

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles (Silver v2.0.0)
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

## Silver Tier Recommended Prompts (copy-paste one by one)

1. "Read spec.constitution.md (Silver). Build on existing Bronze vault. Create new folders: /Pending_Approval, /Approved, /Rejected. Update Dashboard.md to show approval queue section. Create agent_skills/approval_skills.md with HITL thresholds."

2. "Implement Gmail Watcher (gmail_watcher.py): Use Google API (minimal deps), poll for unread important emails every 120s, create Needs_Action/EMAIL_*.md with frontmatter + snippet. Include OAuth setup comments."

3. "Create basic MCP for email: email_mcp.py (Python) that sends/drafts Gmail using credentials from .env. Dry-run mode first. Integrate with orchestrator."

4. "Update orchestrator script: Claim-by-move from Needs_Action → In_Progress → call Claude Code → parse plan for HITL → create Pending_Approval if needed → wait for move to Approved → execute MCP."

5. "Add Ralph Wiggum basic loop to orchestrator: Re-prompt Claude if no TASK_COMPLETE after 20 iterations."

6. "Add simple LinkedIn post skill: agent_skills/social_post_skills.md + Claude drafts post in Plan.md. (For now, output draft; MCP post later if API easy.)"

7. "Implement basic scheduling: Python loop or cron comment to generate Monday CEO Briefing from /Done tasks."

Test end-to-end after each milestone: Drop email simulation or real → approval → send/log.

---

**Follow this file strictly until Silver Tier is complete.**
After Silver is done, we will update both constitution and these instructions for Gold.

## Active Technologies
- Python 3.8+ (stdlib + minimal pip) — pathlib, time, datetime, os, json, subprocess
- google-api-python-client + google-auth-oauthlib — Gmail API access (002-silver-tier-assistant)
- python-dotenv — .env loading for secrets (002-silver-tier-assistant)
- Local filesystem — Markdown + JSONL files in `AI_Employee_Vault/` directory hierarchy
- MCP server — email_mcp.py for Gmail send/draft operations (002-silver-tier-assistant)

## Recent Changes
- 001-bronze-tier-foundation: Bronze Tier completed (vault, watcher, plan generation)
- Silver upgrade: Constitution v2.0.0, CLAUDE.md updated for Silver rules
