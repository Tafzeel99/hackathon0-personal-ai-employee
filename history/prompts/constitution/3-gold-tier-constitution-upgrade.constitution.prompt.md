---
id: 3
title: Gold Tier Constitution Upgrade
stage: constitution
date: 2026-02-14
surface: agent
model: claude-opus-4-6
feature: none
branch: 002-silver-tier-assistant
user: tafzeel
command: /sp.constitution
labels: ["constitution", "gold-tier", "governance", "odoo", "social", "audit", "resilience"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - No unresolved placeholder tokens (validated via grep)
  - Version line matches Sync Impact Report (3.0.0)
  - Dates in ISO format (2026-02-14)
  - All principles declarative and testable (MUST/SHOULD language)
---

## Prompt

/sp.constitution
Project: Personal AI Employee – Gold Tier Autonomous Employee
Hackathon 0: Building Autonomous FTEs in 2026

Core principles:
- Fully autonomous within safe boundaries: proactive across personal + business domains
- ERP-grade accounting: Odoo Community as local source of truth for finances
- Multi-channel social presence: LinkedIn/FB/IG/X posting + intelligent summaries
- Robust resilience: error recovery, graceful degradation, comprehensive auditing
- Local-first extreme: no cloud sync of secrets/sessions; HITL mandatory for irreversible actions
- Full auditability: immutable, timestamped, detailed logs for every decision/action
- Documentation as artifact: architecture.md + lessons_learned.md must be generated

Key standards:
- Odoo integration: Self-hosted Odoo 19+ Community (local VM or Docker), MCP via JSON-RPC for draft invoices/payments (HITL for confirm/post)
- Social MCPs: At least 3 (FB Graph API, Instagram Business API, X API v2) – post + fetch recent activity for summaries
- Weekly Audit: Sunday night trigger → full review of Odoo transactions + /Done tasks → generate detailed CEO Briefing with revenue calc, bottleneck analysis, proactive suggestions
- Ralph Wiggum: Full persistence loop (file-move completion check preferred over promise) for complex multi-step tasks
- Error handling: Retry with exponential backoff, quarantine bad data, watchdog process restarts, alert files in vault on critical failures
- Logging: /Logs/YYYY-MM-DD.json – append-only, includes full context (prompt, response snippet, MCP call params, outcome)
- Agent Skills expansion: odoo_skills.md, social_summary_skills.md, audit_skills.md, recovery_skills.md
- Claim-by-move strict: only one active task per domain to prevent race conditions
- HITL escalation: All Odoo posts, new social replies, payments > threshold, unusual patterns

Constraints:
- Scope: Gold Tier only – no Platinum cloud hybrid yet
- Odoo: Must be self-hosted locally (not cloud), use JSON-RPC external API
- Social posting: Use official APIs (no scraping); X posting may require paid tier – fallback to draft if blocked
- Dependencies: Add odoorpc or xmlrpc lib for Odoo, facebook-sdk/instagram-api if simple, tweepy or requests-oauthlib for X
- No direct credential exposure: .env + secrets manager hints
- Vault sync: Git for version control (optional but recommended for audit trail)
- Max Claude iterations: 50 per Ralph loop; hard fail + alert after
- Documentation: At end, generate architecture.md (diagram in ASCII/Mermaid) + lessons_learned.md

Success criteria:
- Odoo running locally → MCP drafts invoice/payment → HITL approve → posted → reflected in vault summary
- Social channels: Claude generates post → MCP posts (or drafts) → fetches recent activity → creates summary in /Briefings or /Plans
- Weekly audit runs autonomously: reads Odoo + vault → produces Monday Briefing with revenue, bottlenecks, suggestions
- Multi-step task (e.g., invoice from WhatsApp/email → Odoo draft → approval → post → social announcement) completes via Ralph loop
- Graceful degradation: API down → queue task locally → resume on restore
- End-to-end demo covers cross-domain (email/WhatsApp trigger → accounting → social post → audit)
- Comprehensive logs allow full reconstruction of any action
- Architecture + lessons documented in vault
- Output exactly when full Gold ready: GOLD TIER AUTONOMOUS EMPLOYEE COMPLETE – READY FOR PLATINUM OR SUBMISSION

Milestone completion phrase:
GOLD MILESTONE COMPLETE: [short description, e.g., Odoo MCP + invoice flow integrated]

## Response snapshot

Updated constitution from Silver v2.0.0 to Gold v3.0.0 (MAJOR bump). Expanded from 6 to 10 principles: added ERP-Grade Accounting (III), Multi-Channel Social Presence (IV), Full Auditability (VII), Documentation as Artifact (VIII). Reframed existing principles for Gold scope. Added key standards for Odoo Integration (JSON-RPC, self-hosted Docker/VM), Social MCPs (FB/IG/X — 3 platforms minimum), Weekly Audit (Sunday night trigger, revenue calc, bottleneck analysis), Error Handling & Resilience (exponential backoff, quarantine, watchdog, alerts), Documentation Artifacts. Raised Ralph Wiggum cap to 50. Relaxed line limit to 200. Added vault folders: Quarantine/, Alerts/. Added 4 new Agent Skills. Expanded HITL escalation triggers. Updated scope boundary table, trigger mechanisms, success criteria, and heritage section.

## Outcome

- ✅ Impact: Constitution upgraded to Gold v3.0.0 with 10 principles covering ERP, social, audit, resilience, and documentation
- 🧪 Tests: Validated no unresolved placeholders, version matches report, ISO dates, declarative language
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Update CLAUDE.md for Gold rules, create Gold feature spec (/sp.specify), then plan and tasks
- 🧠 Reflection: Gold is a significant scope expansion (Odoo + 3 social APIs + audit + resilience). Keeping the same architectural patterns (folder-based HITL, Agent Skills, claim-by-move) ensures consistency despite complexity growth.

## Evaluation notes (flywheel)

- Failure modes observed: None — clean upgrade from existing template
- Graders run and results (PASS/FAIL): Placeholder validation PASS, version check PASS, template compatibility check PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Validate that CLAUDE.md Gold update references all 10 principles correctly
