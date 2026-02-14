# Lessons Learned — Gold Tier

**Version**: Gold v3.0.0 | **Generated**: 2026-02-15

## 1. Agent Skills Pattern Works Exceptionally Well

Separating intelligence (Markdown files) from mechanics (Python scripts) was the single best architectural decision. Adding new capabilities (Odoo, social, audit) never required modifying the orchestrator's core logic — only adding new `.md` skill files and new MCP scripts. Claude reads the skills at invocation time, keeping intelligence flexible and auditable.

**Recommendation for Platinum**: Continue this pattern for any new domain. Consider versioning skill files if they need to evolve without breaking existing behavior.

## 2. Folder-Based HITL Scales Surprisingly Well

The `Pending_Approval/ → Approved/ / Rejected/` workflow is dead simple and scales to every new action type (email, Odoo, 3 social platforms) without any architectural change. The filesystem IS the state machine. No database, no API, no race conditions (claim-by-move is atomic on most filesystems).

**What surprised us**: Even multi-step tasks (Odoo invoice → social announcement) work cleanly by creating separate approval files per step.

## 3. Retry + Quarantine is Essential for Multi-API Systems

Gold integrates with 5+ external APIs (Gmail, Odoo, Facebook, Instagram, X/Twitter). Any of them can fail at any time. The retry handler with exponential backoff catches transient issues (rate limits, temporary outages), and the quarantine pattern prevents failed tasks from blocking the entire pipeline.

**Key insight**: Domain-level health tracking (the `_domain_failures` counter) prevents wasting retries on a known-down API while keeping other domains operational.

## 4. X/Twitter Paid Tier Fallback Was the Right Call

Twitter's API v2 requires a paid Basic tier ($100/month) for write access. Building the draft fallback into `social_x_mcp.py` from day one meant we never blocked on this dependency. The system degrades gracefully: draft file in `Plans/` with a "manual posting required" note.

**Decision we'd keep**: Always build fallbacks for external dependencies that might be unavailable. Never let a third-party limitation block the entire flow.

## 5. The Constitution as Living Document

Having a single constitution file (`spec.constitution.md`) that defines all rules, constraints, and patterns made Gold development predictable. Every design question could be answered by reading the constitution. The version bump from Silver (v2.0.0) to Gold (v3.0.0) was clean because we documented what changed and why.

**What we'd do differently**: Write the constitution's error-handling section FIRST, before implementing any API integration. We ended up retrofitting retry/quarantine patterns that should have been foundational from the start.

## 6. Watchdog Needs Anti-Restart-Loop Protection

A naive watchdog that restarts processes immediately can create restart loops if the underlying issue is persistent (e.g., missing credentials, port conflict). The 3-restarts-in-5-minutes cap prevents this, but we initially forgot to add it.

**Key learning**: Any auto-restart mechanism MUST have a circuit breaker.

## 7. Structured Logging Pays Off During Audits

Gold's logging with rich detail fields (`mcp_params`, `odoo_record_id`, `social_post_id`, `retry_count`) makes the weekly audit possible. Without these fields, the audit generator would have no data to work with. The JSONL format (one file per day, append-only) is simple and reliable.

**What worked**: `log_utils.py` accepting both string and dict details maintained backward compatibility while enabling rich Gold logging.

## 8. Multi-Step Tasks Are the Hardest Part

Cross-domain tasks (invoice → social post) require careful state tracking across multiple HITL approval gates. Each step depends on the previous step's completion. The `.state_*.json` approach works for tracking, but a more robust state machine would be better for complex workflows.

**Recommendation for Platinum**: Consider a lightweight state machine library or a dedicated workflow file format for multi-step tasks.

## 9. Keep Scripts Under 200 Lines

The relaxed line limit (200 from Silver's 150) was necessary for complex MCP integrations, but staying under it forced good modular design. `orchestrator.py` is the densest file and benefits from the extracted `retry_handler.py` and `quarantine_utils.py` utilities.

**Pattern**: Extract cross-cutting concerns into utility modules. Keep domain-specific logic in MCP scripts.

## 10. Incremental Tier Approach Reduces Risk

Building Bronze → Silver → Gold in sequence, with each tier building on the previous, meant we never had to redesign the foundation. Silver's folder workflow, watchers, and orchestrator pattern were reused intact. Gold added new MCPs and skills without modifying the proven patterns.

**Recommendation for Platinum**: Maintain this approach. Platinum should extend Gold, not replace it.
