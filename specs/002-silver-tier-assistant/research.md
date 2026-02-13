# Research: Silver Tier Functional Assistant

**Branch**: `002-silver-tier-assistant` | **Date**: 2026-02-13

## Technology Decisions

### T-001: Gmail API Authentication Method

**Decision**: Use `google-auth-oauthlib` with OAuth 2.0 installed app flow
(desktop/CLI credentials).

**Rationale**: The Gmail API requires OAuth 2.0 for user mailbox access.
Service accounts cannot access personal Gmail. The "installed app" flow
generates a `credentials.json` (downloaded from Google Cloud Console) and
creates a `token.json` after first-time browser-based consent. Subsequent
runs reuse the token silently. This is the simplest path for a single-user
local app.

**Alternatives considered**:
- **Service Account**: Cannot access personal Gmail mailboxes — only works
  with Google Workspace domain-wide delegation. Rejected.
- **App Passwords (IMAP)**: Google is deprecating less-secure app access.
  Unreliable. Rejected.
- **Raw `requests` library**: Possible but requires manual OAuth token
  refresh logic. More code, same result. Rejected.

**Dependencies**: `google-api-python-client`, `google-auth-oauthlib`,
`google-auth-httplib2`

### T-002: Gmail Watcher Polling vs Push

**Decision**: Use polling (list unread messages every 120 seconds).

**Rationale**: Push notifications require a publicly accessible webhook
endpoint (Cloud Pub/Sub), which violates the local-first constraint and
adds cloud infrastructure. Polling every 120 seconds is simple, stays under
Gmail API daily quota (10,000 queries/day = ~7/minute budget), and matches
the existing filesystem watcher pattern.

**Alternatives considered**:
- **Google Cloud Pub/Sub push**: Requires cloud infrastructure, public
  endpoint, subscription management. Violates local-first principle.
  Rejected.
- **IMAP IDLE**: Requires persistent socket connection, less reliable on
  consumer networks, and Google recommends the REST API for new apps.
  Rejected.

### T-003: Email MCP Architecture

**Decision**: Implement email MCP as a standalone Python script
(`email_mcp.py`) that the orchestrator calls via `subprocess`.

**Rationale**: The MCP (Model Context Protocol) pattern in this project is
a simple "callable service" — the orchestrator reads an approved action
file, extracts parameters, and calls the MCP script with those parameters.
The MCP script handles Gmail API interaction (send/draft) and returns a
result. This keeps the orchestrator agnostic to the API details and allows
swapping MCP implementations without changing the orchestrator.

**Alternatives considered**:
- **HTTP server MCP**: Running a local HTTP server adds complexity (Flask,
  port management, process lifecycle). Violates "Cost & Simplicity."
  Rejected.
- **Inline function in orchestrator**: Tightly couples email logic to
  orchestrator. Violates "Modularity" principle. Rejected.
- **Node.js MCP**: Adds a language dependency. Python is already the
  project language. Rejected.

### T-004: Orchestrator Claim-by-Move Atomicity

**Decision**: Use `shutil.move()` for claim-by-move. Accept that this is
not truly atomic on all filesystems but is sufficient for single-user
single-process use.

**Rationale**: True atomic file operations require OS-level primitives
(`rename()` on same filesystem, `flock()`). Since Silver Tier is single-
user on a local machine, `shutil.move()` provides adequate isolation.
The edge case of two orchestrator instances is documented but is a user
error, not a design flaw. If the file disappears mid-move (already
claimed), a `FileNotFoundError` is caught and the orchestrator skips
that task.

**Alternatives considered**:
- **File locking (`fcntl.flock`)**: Platform-dependent (not available on
  Windows). Adds complexity for minimal benefit in single-user scenario.
  Rejected.
- **Database-based locking**: Violates local-first (no databases in
  Silver). Rejected.

### T-005: Ralph Wiggum Loop Implementation

**Decision**: Implement as a Python `for` loop (max 20 iterations) in
`orchestrator.py` that calls Claude Code CLI via `subprocess.run()`,
checking for `TASK_COMPLETE` in stdout after each iteration.

**Rationale**: The loop pattern is intentionally simple: invoke Claude Code
with the task context, capture output, check for the completion marker. If
found, break. If not, re-invoke with the same context plus any new files
Claude created. The iteration cap (20) is hardcoded as a constant with a
comment referencing the constitution. This prevents infinite loops without
requiring complex state management.

**Alternatives considered**:
- **Recursive function**: Risk of stack overflow on deep recursion. No
  benefit over a loop. Rejected.
- **Event-driven (asyncio)**: Overkill for sequential task processing.
  Rejected.

### T-006: Logging Format

**Decision**: JSONL (one JSON object per line) in `Logs/YYYY-MM-DD.json`.
Use Python `json` module to serialize, append with `open(file, 'a')`.

**Rationale**: JSONL is simple to write (append-only), simple to read
(line-by-line parsing), and compatible with tools like `jq`. No external
libraries needed. One file per day keeps files manageable and enables
easy date-based queries.

**Alternatives considered**:
- **Single JSON array file**: Requires reading + parsing entire file to
  append. Fragile on crash (incomplete array). Rejected.
- **SQLite**: Adds complexity and a binary format. Violates "no databases"
  constraint. Rejected.
- **Python `logging` module**: Text-oriented, not structured. Would need
  custom formatter. More complex than direct JSON writes. Rejected.

### T-007: LinkedIn Post Approach

**Decision**: Draft-only in Silver Tier. Claude generates the post text in
Plan.md. The draft is placed in `Pending_Approval/` for human review.
After approval, the content is logged as "ready for posting" — the human
copies and pastes to LinkedIn manually.

**Rationale**: LinkedIn API requires a LinkedIn Developer App with OAuth
2.0, company page access, and review process for posting permissions. This
is too heavy for Silver Tier. Draft-only delivers 80% of the value (time
saved on content creation) with zero API complexity.

**Alternatives considered**:
- **LinkedIn API integration**: Requires developer app registration,
  OAuth flow, and LinkedIn review process. Too heavy for hackathon. Deferred
  to Gold.
- **Browser automation (Playwright)**: Explicitly out of scope per
  constitution. Rejected.

### T-008: Scheduling Mechanism

**Decision**: Use a simple `while True` + `time.sleep()` loop in the
orchestrator script that checks the current day/time and triggers briefing
generation when the schedule matches (e.g., Monday at startup or on-demand
via CLI flag `--generate-briefing`).

**Rationale**: System cron is platform-dependent (Linux cron vs Windows
Task Scheduler). A Python-based check inside the already-running
orchestrator is portable and requires zero external configuration. The
`--generate-briefing` flag allows manual triggering for demos.

**Alternatives considered**:
- **System cron**: Platform-dependent. Requires user to configure cron
  separately. Rejected for Silver (acceptable in Gold).
- **`schedule` library**: Extra pip dependency for minimal benefit (one
  scheduled task). Rejected.
- **Standalone scheduled script**: Would need its own process management.
  Simpler to integrate into orchestrator. Rejected.

### T-009: python-dotenv vs os.environ

**Decision**: Use `python-dotenv` to load `.env` file. Fall back to
`os.environ` if `python-dotenv` is not installed.

**Rationale**: `python-dotenv` provides a clean `load_dotenv()` call that
reads `.env` at startup without requiring the user to `export` variables
manually. This is standard practice for local development. The fallback
to `os.environ` ensures the scripts work in environments where `.env`
is sourced by the shell instead.

**Dependencies**: `python-dotenv` (pip install)
