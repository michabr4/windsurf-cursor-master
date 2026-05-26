# ServiceFlow SDM — Required Cisco Data Sources

> Reverse-engineered from the application design (database schema, env config, integration modules, frontend pages, and feature flags).
> Analysis date: 2026-04-03

---

## Overview

The design calls for **5 dedicated Cisco integration modules** (backend directory: `src/integrations/{tac,dna-center,smart-licensing,webex,teams}`). By tracing every database column, environment variable, feature flag, and frontend page back to its upstream system, we can identify **6 distinct Cisco API families** plus **2 implied Cisco data feeds** that don't have explicit env vars but whose data fields are present in the schema.

---

## Data Source 1: Cisco TAC Service Request API

**Integration module:** `src/integrations/tac/`
**Base URL:** `https://tools.cisco.com/tac/api/v2`
**Auth:** API key + secret (`TAC_API_KEY`, `TAC_API_SECRET`)
**Contract:** `GES-W-2024-MGM`
**Feature flag:** `ENABLE_TAC_AUTO_CREATE`

### What the app stores (→ what the API must supply)

| DB Table | Fields sourced from TAC API |
|---|---|
| `cisco.tac_cases` | `case_number`, `severity`, `status`, `sub_status`, `product_family`, `product_series`, `problem_type`, `problem_code`, `technology`, `tac_engineer_name`, `tac_engineer_email`, `tac_engineer_phone`, `tac_engineer_cco_id`, `resolution`, `resolution_code`, `related_bug_ids[]`, `escalation_level`, `first_response_at`, `last_update_at`, `resolved_at`, `closed_at` |
| `cisco.tac_case_updates` | `update_type`, `content`, `author`, `author_type` (customer/tac/system), `attachments` |
| `mgm.incidents` | `tac_case_number`, `tac_case_id`, `tac_severity` (cross-linked) |
| `mgm.sla_metrics` | `tac_cases_opened`, `tac_cases_closed`, `tac_avg_response_minutes`, `tac_avg_resolution_hours` |

### Required API Operations

| Operation | Direction | Trigger |
|---|---|---|
| **Create** SR | App → TAC | `ENABLE_TAC_AUTO_CREATE` flag; auto-open TAC case when P1/P2 incident created |
| **Read** SR list | TAC → App | Sync open cases for contract `GES-W-2024-MGM` |
| **Read** SR detail | TAC → App | Pull engineer assignment, status updates, resolution |
| **Update** SR (add note) | App → TAC | Push customer updates / attachments from incident workflow |
| **Read** SR updates/history | TAC → App | Populate `tac_case_updates` timeline |
| **Webhook/poll** | TAC → App | Detect status changes, escalation events (for real-time notifications) |

### Actual Cisco API

**Cisco Support APIs — Service Request API v3**
- Portal: `https://apiconsole.cisco.com`
- Docs: Cisco DevNet — Support APIs
- Entitlement: Requires active service contract + API Console access

---

## Data Source 2: Cisco DNA Center (Catalyst Center)

**Integration module:** `src/integrations/dna-center/`
**Base URL:** `https://{DNA_CENTER_HOST}:443`
**Auth:** Username + password (basic → token exchange)

### What the app stores (→ what DNAC must supply)

| DB Table | Fields sourced from DNA Center |
|---|---|
| `mgm.devices` | `hostname`, `ip_address`, `ipv6_address`, `mac_address`, `serial_number`, `device_type`, `device_category`, `model`, `software_version`, `hardware_revision`, `location`, `role`, `status`, `health_score`, `cpu_utilization`, `memory_utilization`, `uptime`, `last_seen`, `last_reboot`, `dna_managed` (boolean), `dna_device_id` |
| `mgm.sla_metrics` | `availability_percent`, `uptime_minutes`, `downtime_minutes` (derived from device health) |
| `mgm.property_technology_adoption` | `devices_deployed`, `health_score`, `health_status` |

### Required API Operations

| Operation | DNAC API Endpoint Family | Purpose |
|---|---|---|
| **Device inventory** | `/dna/intent/api/v1/network-device` | Full device list with model, serial, SW version, role, location |
| **Device detail** | `/dna/intent/api/v1/network-device/{id}` | Per-device deep attributes |
| **Device health** | `/dna/intent/api/v1/device-health` | Health score (0–100), CPU, memory, uptime |
| **Site hierarchy** | `/dna/intent/api/v1/site` | Map devices → MGM properties via DNAC site/building/floor |
| **Client health** | `/dna/intent/api/v1/client-health` | Wireless/wired client metrics per property |
| **Issue/assurance** | `/dna/intent/api/v1/issues` | Proactive issue detection → auto-create incidents |
| **Command runner** | `/dna/intent/api/v1/network-device-poller/cli/read-request` | On-demand device diagnostics for incident triage |

### Sync Pattern
- **Scheduled sync** (cron via `node-cron` / `bull` queue): periodic full device inventory pull
- **Event-driven**: DNAC webhooks for health score changes, new issues → real-time WebSocket push to frontend

---

## Data Source 3: Cisco Smart Software Manager (SSM)

**Integration module:** `src/integrations/smart-licensing/`
**Token URL:** `https://cloudsso.cisco.com/as/token.oauth2`
**API URL:** `https://swapi.cisco.com/services/api/smart-accounts-and-licensing`
**Auth:** OAuth 2.0 client credentials (`SMART_LICENSING_CLIENT_ID`, `SMART_LICENSING_CLIENT_SECRET`)

### What the app stores (→ what SSM must supply)

| DB Table | Fields sourced from SSM |
|---|---|
| `cisco.licenses` | `license_type`, `product_family`, `product_name`, `sku`, `quantity_purchased`, `quantity_consumed`, `quantity_reserved`, `license_model`, `start_date`, `expiry_date`, `renewal_date`, `smart_account`, `virtual_account`, `status`, `compliance_status`, `auto_renewal` |
| `cisco.license_history` | `event_type`, `quantity_change`, `old/new_quantity`, `old/new_expiry_date` |
| `mgm.property_license_usage` | `quantity_used`, `device_count`, `user_count`, `last_sync`, `sync_source` |
| `mgm.devices` | `smart_license_status`, `license_level` |

### Required API Operations

| Operation | Purpose |
|---|---|
| **List Smart Accounts** | Enumerate accounts tied to GES-West contract |
| **List Virtual Accounts** | Map VAs to MGM properties |
| **License entitlements** | Pull purchased quantities, SKUs, expiry dates per VA |
| **License consumption** | Current consumed/reserved counts, compliance status |
| **License usage by device** | Which serial numbers are consuming which licenses |
| **Renewal notifications** | Approaching expiry (feeds `license_expiry` notification type) |

### Alerts Generated
- `notification_type = 'license_expiry'` when expiry within `renewal_window_days` (default 90)
- `alert_threshold` at 80% utilization → dashboard warning

---

## Data Source 4: Cisco WebEx APIs

**Integration module:** `src/integrations/webex/`
**Auth:** Bot token (`WEBEX_BOT_TOKEN`) + OAuth 2.0 for user context
**Webhook:** Inbound events signed with `WEBEX_WEBHOOK_SECRET`

### What the app stores (→ what WebEx must supply)

| DB Table | Fields sourced from WebEx |
|---|---|
| `mgm.webex_spaces` | `webex_space_id`, `space_title`, `meeting_url`, `meeting_number`, `meeting_password`, `participants[]`, `recording_urls[]`, `started_at`, `ended_at` |
| `cisco.tac_cases` | `webex_space_id`, `war_room_url` (cross-linked to war room space) |
| `mgm.incidents` | `webex_space_id` (incident-specific collaboration space) |

### Required API Operations

| Operation | Purpose |
|---|---|
| **Create space** | Auto-create war rooms for P1/P2 incidents and TAC escalations |
| **Add members** | Add SDM, TAC engineer, MGM IT manager, assigned engineer to space |
| **Post message** | Push incident status updates, TAC case updates into space |
| **Create meeting** | Spin up ad-hoc meetings for war rooms |
| **List recordings** | Archive meeting recordings for post-incident review |
| **Webhooks** (inbound) | Receive message events from spaces for bot command processing |
| **Adaptive cards** | Rich interactive messages for incident acknowledgment/updates |

---

## Data Source 5: Cisco Service Contract / EoX Lifecycle APIs (IMPLIED)

**No explicit integration module or env vars defined** — but the database schema contains fields that can only come from Cisco's contract and product lifecycle databases.

### Evidence in the schema

| DB Table | Fields requiring this source |
|---|---|
| `mgm.devices` | `contract_number`, `contract_type`, `contract_start_date`, `contract_expiry`, `warranty_expiry`, `eol_date`, `eos_date` |
| `cisco.tac_cases` | `contract_number` (validated against active contract for TAC entitlement) |

### Required Cisco APIs

| API | Cisco DevNet Name | Data Provided |
|---|---|---|
| **Service Contract API** | Cisco Support APIs — Serial Number to Contract | Contract coverage status, contract type, start/end dates per serial number |
| **EoX API** | Cisco Support APIs — EoX (End of Life) | End-of-Life (EoL), End-of-Sale (EoS), End-of-SW-Maintenance, Last-Day-of-Support dates per PID |
| **Warranty API** | Cisco Support APIs — Serial Number to Warranty | Warranty type, coverage start/end per serial number |

### How it feeds the app
- After device inventory sync from DNA Center, a **secondary enrichment job** should query each device's serial number against these APIs to populate contract/lifecycle fields
- Drives proactive alerts: devices approaching EoL/EoS, contracts expiring, warranty lapsing

---

## Data Source 6: Cisco Bug Search Tool API (IMPLIED)

**No explicit env vars defined** — but `cisco.tac_cases.related_bug_ids TEXT[]` stores bug IDs, and TAC resolutions frequently reference Cisco bug CSCxx numbers.

### Evidence in the schema

| DB Table | Field |
|---|---|
| `cisco.tac_cases` | `related_bug_ids TEXT[]` — array of CSCxx bug IDs |

### Required Cisco API

| API | Purpose |
|---|---|
| **Cisco Bug API** (DevNet Support APIs) | Resolve bug IDs to title, severity, affected versions, fix versions, workaround. Display bug details alongside TAC case resolution in the incident timeline. |

---

## Data Source Summary Matrix

| # | Data Source | Cisco API Family | Auth Model | Explicit in Design? | Tables Fed |
|---|---|---|---|---|---|
| 1 | **TAC Service Request** | Support APIs — SR API v3 | API key + secret | YES (env, module, flag) | `cisco.tac_cases`, `cisco.tac_case_updates`, `mgm.incidents`, `mgm.sla_metrics` |
| 2 | **DNA Center** | DNAC Platform APIs | Basic → token | YES (env, module) | `mgm.devices`, `mgm.sla_metrics`, `mgm.property_technology_adoption` |
| 3 | **Smart Licensing (SSM)** | SWAPI — Smart Accounts | OAuth 2.0 CC | YES (env, module) | `cisco.licenses`, `cisco.license_history`, `mgm.property_license_usage`, `mgm.devices` |
| 4 | **WebEx** | WebEx REST APIs | Bot token + OAuth | YES (env, module) | `mgm.webex_spaces`, `cisco.tac_cases`, `mgm.incidents` |
| 5 | **Service Contract / EoX** | Support APIs — SN2Contract, EoX, Warranty | API key | IMPLIED (schema fields, no env) | `mgm.devices` |
| 6 | **Bug Search Tool** | Support APIs — Bug API | API key | IMPLIED (schema field) | `cisco.tac_cases` |

---

## Data Flow Diagram (Text)

```
                          ┌─────────────────────────────────────┐
                          │        CISCO DATA SOURCES           │
                          └──────────────┬──────────────────────┘
                                         │
         ┌───────────┬──────────┬────────┼────────┬──────────┬───────────┐
         ▼           ▼          ▼        ▼        ▼          ▼           ▼
    ┌─────────┐ ┌────────┐ ┌───────┐ ┌──────┐ ┌───────┐ ┌───────┐ ┌────────┐
    │  TAC SR │ │  DNAC  │ │  SSM  │ │WebEx │ │SN2Cont│ │  EoX  │ │Bug API │
    │  API    │ │ APIs   │ │ SWAPI │ │ APIs │ │  API  │ │  API  │ │        │
    └────┬────┘ └───┬────┘ └───┬───┘ └──┬───┘ └───┬───┘ └───┬───┘ └───┬────┘
         │          │          │        │         │         │         │
         ▼          ▼          ▼        ▼         ▼         ▼         ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │              ServiceFlow SDM Backend (Node.js/Express)              │
    │   src/integrations/{tac, dna-center, smart-licensing, webex}        │
    │   + bull queues + node-cron for scheduled sync                      │
    └────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                     PostgreSQL 15                                    │
    │  ┌─────────┐  ┌────────────┐  ┌───────────────────────────────┐    │
    │  │  cisco.  │  │    mgm.    │  │          audit.               │    │
    │  │tac_cases │  │  devices   │  │       activity_log            │    │
    │  │licenses  │  │ incidents  │  └───────────────────────────────┘    │
    │  │technol.  │  │sla_metrics │                                       │
    │  └─────────┘  │ properties │                                       │
    │               │webex_spaces│                                       │
    │               └────────────┘                                       │
    └─────────────────────────────────────────────────────────────────────┘
                                 │
                          ┌──────┴──────┐
                          ▼             ▼
                    ┌──────────┐  ┌──────────┐
                    │ Frontend │  │  Mobile   │
                    │  React   │  │React Natv │
                    └──────────┘  └──────────┘
```

---

## Gap Analysis: What the Design Implies But Doesn't Provision

| Gap | Missing Element | Impact |
|---|---|---|
| **No env vars for Support APIs** (Contract/EoX/Bug/Warranty) | Need `CISCO_SUPPORT_API_KEY` + `CISCO_SUPPORT_API_SECRET` in `.env` | Cannot populate `eol_date`, `eos_date`, `warranty_expiry`, `contract_*` on devices, or resolve `related_bug_ids` |
| **No PSIRT/openVuln integration** | The Security technology category exists but no vulnerability feed | No proactive security advisory correlation with device inventory |
| **No Meraki integration** | If any MGM properties use Meraki (common in hospitality), the design is pure DNA Center | Would miss a significant device population |
| **No ThousandEyes / AppDynamics** | The Observability category in `cisco.technologies` has no API backing | SLA availability metrics would need manual input or a separate feed |
| **Phases 4–8 missing** | Integration layer (Phase 6) was not included in the document | The actual API client code, polling logic, error handling, and retry patterns are undefined |

---

*Generated from design analysis on 2026-04-03.*
