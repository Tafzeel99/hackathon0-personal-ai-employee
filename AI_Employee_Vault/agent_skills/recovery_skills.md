# Recovery Skills — Gold Tier

You are handling error recovery, graceful degradation, and system resilience.
Follow these rules exactly.

## Retry Policy

When an external API call fails with a transient error:

1. **Transient errors** (safe to retry): HTTP 429, 500, 502, 503, 504, connection timeouts, rate limits
2. **Non-transient errors** (do NOT retry): HTTP 400, 401, 403, 404, validation errors, auth failures
3. **Backoff schedule**: 1 second → 2 seconds → 4 seconds (exponential, doubles each time)
4. **Maximum retries**: 3 attempts total
5. **Maximum delay**: 60 seconds (cap for any single wait)
6. **Log each retry**: Include attempt number, delay, and error message

## Quarantine Criteria

Move a task to `Quarantine/` when:

- All retry attempts are exhausted (3 failures for transient errors)
- A non-transient error occurs that cannot be resolved automatically
- The task data is malformed or missing required fields
- An external system returns a permanent error (e.g., "resource deleted", "account suspended")

Quarantine file MUST include:
- Original task content preserved
- `status: quarantined` in frontmatter
- `quarantined: <ISO-8601 timestamp>` in frontmatter
- Error details as HTML comment block after frontmatter

## Alert File Format

Create an alert in `Alerts/` when:

- A task is quarantined (always)
- A process crashes and watchdog restarts it
- Authentication/credentials expire
- An API is down for more than 3 consecutive check cycles
- Disk space is critically low

Alert file structure:
```yaml
---
type: alert
created: <ISO-8601>
component: <which script/MCP failed>
severity: critical
status: open
---
```

Body MUST contain:
- **Title**: Clear one-line description
- **Component**: Which part of the system failed
- **Description**: What happened, including error details
- **Suggested Remediation**: Specific steps the human should take

## Watchdog Behavior

The watchdog (`watchdog_monitor.py`) monitors processes by PID file:

1. Check every 15 seconds if monitored processes are alive
2. If a process is not running, restart it via `subprocess.Popen`
3. Log every restart event
4. If restart fails, create an alert in `Alerts/`
5. Do NOT restart more than 3 times in 5 minutes (prevent restart loops)

## Graceful Degradation Rules

When one API/domain is down:

1. **Continue processing other domains** — if Odoo is down, still process emails and social tasks
2. **Queue, don't discard** — leave tasks for the down domain in `Needs_Action/` (do not claim them)
3. **Resume automatically** — when the API responds again, resume normal processing
4. **Notify** — create a single alert per outage, not per failed task

## Error Classification

| Error Type | Action | Retry? |
|---|---|---|
| HTTP 429 (rate limit) | Retry with backoff, respect Retry-After header | Yes |
| HTTP 500/502/503/504 | Retry with backoff | Yes |
| HTTP 401/403 (auth) | Alert + quarantine (credentials may be expired) | No |
| HTTP 400 (bad request) | Quarantine (data issue) | No |
| Connection timeout | Retry with backoff | Yes |
| DNS resolution failure | Alert + quarantine | No |
| Odoo JSON-RPC error | Check error code: retry if server error, quarantine if validation | Depends |
| Social API rate limit | Respect platform cooldown window, retry after | Yes |
