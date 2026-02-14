# Gold Tier Architecture — Personal AI Employee

**Version**: Gold v3.0.0 | **Generated**: 2026-02-15

## System Diagram

```mermaid
graph TD
    subgraph Triggers
        FS[filesystem_watcher.py<br/>Polls watch_inbox/ every 15s]
        GM[gmail_watcher.py<br/>Polls Gmail every 120s]
        SCH[Scheduled Trigger<br/>Sunday audit, recurring tasks]
    end

    subgraph Vault["AI_Employee_Vault/"]
        WI[watch_inbox/]
        NA[Needs_Action/]
        IP[In_Progress/]
        PL[Plans/]
        PA[Pending_Approval/]
        AP[Approved/]
        RJ[Rejected/]
        DN[Done/]
        BR[Briefings/]
        OD[Odoo_Drafts/]
        QR[Quarantine/]
        AL[Alerts/]
        LG[Logs/]
        SK[agent_skills/]
    end

    subgraph Orchestrator
        ORC[orchestrator.py<br/>Claims tasks, invokes Claude,<br/>handles HITL, dispatches MCPs]
        RL[Ralph Wiggum Loop<br/>Max 50 iterations<br/>File-move completion check]
    end

    subgraph MCPs["MCP Servers"]
        EM[email_mcp.py<br/>Gmail send/draft]
        OO[odoo_mcp.py<br/>JSON-RPC to Odoo]
        FB[social_facebook_mcp.py<br/>Graph API post + fetch]
        IG[social_instagram_mcp.py<br/>Business API post + fetch]
        XM[social_x_mcp.py<br/>API v2 post + fetch]
    end

    subgraph External["External Services"]
        GMAIL[Gmail API]
        ODOO[Odoo Community 19+<br/>Self-hosted, JSON-RPC]
        FBG[Facebook Graph API]
        IGG[Instagram Business API]
        XAP[X/Twitter API v2]
    end

    subgraph Support["Support Services"]
        WD[watchdog_monitor.py<br/>Process monitor, 15s poll]
        RH[retry_handler.py<br/>Exponential backoff]
        QU[quarantine_utils.py<br/>Task quarantine + alerts]
        LU[log_utils.py<br/>JSONL structured logging]
        AG[audit_generator.py<br/>Weekly 5-section audit]
    end

    %% Trigger flows
    FS -->|"New file"| NA
    GM -->|"New email"| NA
    SCH -->|"Sunday"| AG

    %% Orchestrator flow
    NA -->|"claim_task()"| IP
    IP -->|"invoke_claude()"| RL
    RL -->|"Plan"| PL
    PL -->|"HITL needed"| PA
    PA -->|"Human moves"| AP
    PA -->|"Human moves"| RJ
    AP -->|"handle_approved()"| ORC
    RJ -->|"handle_rejected()"| DN

    %% MCP dispatch
    ORC -->|"email_send"| EM
    ORC -->|"odoo_confirm"| OO
    ORC -->|"post_facebook"| FB
    ORC -->|"post_instagram"| IG
    ORC -->|"post_x"| XM

    %% External connections
    EM --> GMAIL
    OO --> ODOO
    FB --> FBG
    IG --> IGG
    XM --> XAP
    GM --> GMAIL

    %% Support connections
    RH -.->|"wraps"| EM
    RH -.->|"wraps"| OO
    RH -.->|"wraps"| FB
    QU -.->|"on failure"| QR
    QU -.->|"on failure"| AL
    WD -.->|"monitors"| FS
    WD -.->|"monitors"| GM
    WD -.->|"monitors"| ORC
    LU -.->|"writes"| LG

    %% Completion
    ORC -->|"complete"| DN
    ORC -->|"Odoo draft"| OD
    AG -->|"audit"| BR

    %% Skills
    SK -.->|"read by Claude"| RL
```

## Component Descriptions

### Watchers (Event Detection)

| Component | File | Purpose | Polling |
|-----------|------|---------|---------|
| Filesystem Watcher | `filesystem_watcher.py` | Detects files dropped into `watch_inbox/` | 15 seconds |
| Gmail Watcher | `gmail_watcher.py` | Detects unread emails via Gmail API | 120 seconds |
| Scheduled Trigger | Built into `orchestrator.py` | Sunday audit, recurring tasks | Per orchestrator cycle |

### Orchestrator (Central Brain)

| Component | File | Purpose |
|-----------|------|---------|
| Orchestrator | `orchestrator.py` | Claims tasks, invokes Claude with agent skills, creates plans, manages HITL workflow, dispatches to MCPs |
| Ralph Wiggum Loop | Inside `orchestrator.py` | Persistence loop for multi-step tasks: max 50 iterations, file-move completion check |

### MCP Servers (External Actions)

| Component | File | External Service | Actions |
|-----------|------|-----------------|---------|
| Email MCP | `email_mcp.py` | Gmail API | Send, draft |
| Odoo MCP | `odoo_mcp.py` | Odoo JSON-RPC | Create/confirm/cancel invoice, create/confirm payment, list, query |
| Facebook MCP | `social_facebook_mcp.py` | Graph API | Post to page, fetch activity |
| Instagram MCP | `social_instagram_mcp.py` | Business API | Post media, fetch activity |
| X/Twitter MCP | `social_x_mcp.py` | API v2 | Post tweet (or draft fallback), fetch activity |

### Support Services

| Component | File | Purpose |
|-----------|------|---------|
| Retry Handler | `retry_handler.py` | Exponential backoff (1s→2s→4s, max 60s, 3 retries) |
| Quarantine Utils | `quarantine_utils.py` | Move failed tasks to `Quarantine/`, create alerts in `Alerts/` |
| Log Utils | `log_utils.py` | JSONL structured logging with rich details |
| Watchdog | `watchdog_monitor.py` | Process monitor — restarts crashed watchers/orchestrator |
| Audit Generator | `audit_generator.py` | Weekly 5-section audit across Odoo + vault + social |
| Briefing Generator | `briefing_generator.py` | Legacy Silver briefing (retained, superseded by audit) |

### Agent Skills (Claude Intelligence)

| Skill | File | Purpose |
|-------|------|---------|
| Planning | `planning_skills.md` | Plan generation rules |
| Email | `email_skills.md` | Email parsing and reply drafting |
| Approval | `approval_skills.md` | HITL routing and thresholds |
| Social Post | `social_post_skills.md` | Multi-platform post drafting (LinkedIn, FB, IG, X) |
| Odoo | `odoo_skills.md` | Invoice/payment creation rules and field mappings |
| Social Summary | `social_summary_skills.md` | Engagement analysis across platforms |
| Audit | `audit_skills.md` | Revenue calculation, bottleneck detection, suggestions |
| Recovery | `recovery_skills.md` | Retry policies, quarantine criteria, degradation rules |

## Data Flow

```
File Drop / Email / Schedule
        │
        ▼
   watch_inbox/ or Gmail API
        │
        ▼
   Needs_Action/ (task file with YAML frontmatter)
        │
        ▼ claim_task() (move to In_Progress/)
   In_Progress/
        │
        ▼ invoke_claude() with agent_skills/
   Plans/ (Plan_*.md with action details)
        │
        ├── No external action → Done/
        │
        └── External action needed
                │
                ▼
        Pending_Approval/ (HITL gate)
                │
                ├── Human approves → Approved/
                │       │
                │       ▼ dispatch_mcp()
                │   MCP Server → External API
                │       │
                │       ▼
                │   Done/ (with result logged)
                │
                └── Human rejects → Rejected/
                        │
                        ▼
                    Done/ (status: rejected)
```

## Integration Points

- **Odoo**: JSON-RPC on `ODOO_URL` (default `http://localhost:8069`), database `ODOO_DB`
- **Gmail**: OAuth 2.0 via `credentials.json` / `token.json`
- **Facebook**: Page Access Token via Graph API v18.0
- **Instagram**: Business Account via Graph API v18.0
- **X/Twitter**: OAuth 1.0a via API v2 (paid tier for posting; free for reading)
- **All credentials**: Stored in `.env` (gitignored), loaded via `python-dotenv`
