# Service Delivery Manager — Required Cisco Data Sources

> Reverse-engineered from the application design (database schema, env config, integration modules, frontend pages, and feature flags).
> Analysis date: 2026-04-03

---

## Overview

The design calls for **5 dedicated Cisco integration modules** (backend directory: `src/integrations/{tac,dna-center,smart-licensing,webex,teams}`). By tracing every database column, environment variable, feature flag, and frontend page back to its upstream system, we can identify **6 distinct Cisco API families** plus **2 implied Cisco data feeds** that don't have explicit env vars but whose data fields are present in the schema.

**Scope extension (aligned with `MVP_SCOPE_FREEZE.md`):** **Waves 5–16** add observability, edge security, flow analytics, optical transport, insights, on-prem collection, identity (including **ISE as Code** policy/config automation on Wave 11), location, SSE posture, **PSIRT / openVuln** advisory and CVE correlation, **Cisco Field Notices** (FN) impact matching, and **Firepower Management Center (FMC)** REST integration for FTD/NGFW inventory and policy context (Wave 16). Each wave needs API Console entitlements (where applicable), env placeholders, and field mapping into `mgm` / `cisco` tables (to be detailed per product API doc).

### Vendor console ↔ MVP wave mapping

Mirrors [MVP_SCOPE_FREEZE.md](MVP_SCOPE_FREEZE.md) **vendor console capability coverage**. **Service Delivery Manager** targets **capability parity** with these consoles via **published APIs only** (no console UI scraping). **Gate** = Cisco API Console (DevNet) entitlements and clients that enable the listed waves.

| Console / operational surface | Wave(s) | Core capability themes (parity target) |
|---|---|---|
| **Cisco API Console (DevNet)** | Gate for 1–16 | OAuth/API clients, contract-scoped API products, entitlement and credential lifecycle |
| **Cisco Catalyst Center** | 1 | Inventory, sites, device health, assurance/issues, diagnostics |
| **Cisco Smart Software Manager / Smart Licensing–class portals** | 3 | Smart Account / Virtual Account alignment, entitlements, consumption, compliance |
| **Cisco Support / TAC & Case Management** | 2, 4 | Service request lifecycle, case detail; contract / EoX / Bug enrichment where APIs exist |
| **WebEx Control Hub–class collaboration** | 4 | Spaces, meetings, incident-linked war-room patterns |
| **ThousandEyes** | 5 | Tests, alerts, paths — org-level service-delivery visibility |
| **Cisco Umbrella** | 6 | Reporting / policy / investigate-class signals (as entitled) |
| **Cisco Secure Network Analytics (Stealthwatch)** | 7 | Flow/security analytics context for triage |
| **Optical / DWDM EMS or equivalent** | 8 | Transport health where managed optical is in scope |
| **Cisco IQ** | 9 | Insights and analytics surfaces (per entitlement) |
| **CSPC / collector deployment** | 10 | Collection and upload alignment with inventory and Smart Account expectations |
| **Cisco ISE Administration + ISE as Code** | 11 | Identity, posture, profiling, policy/config automation |
| **Cisco Spaces** | 12 | Location, occupancy, digital experience where deployed |
| **Cisco Secure Access** | 13 | SSE/ZTNA posture and connectivity diagnostics |
| **PSIRT / OpenVuln & security advisory interfaces** | 14 | Advisory and CVE exposure vs inventory |
| **Cisco Field Notice channels** | 15 | FN impact on PIDs, serials, and software in estate |
| **Cisco Firepower Management Center (FMC)** | 16 | FTD inventory, access policies, objects — REST API parity |
| **Meraki Dashboard** | *Out of MVP* | Excluded unless promoted ([MVP_SCOPE_FREEZE.md](MVP_SCOPE_FREEZE.md) Out of Scope) |
| **AppDynamics** | *Out of MVP* | Excluded unless promoted |

### SDC program consoles → SDM surfaces (personas)

Key **Service Delivery Cloud (SDC)**-class program consoles map to **Service Delivery Manager** views and integration waves (no UI scraping; APIs only).

| SDC / program console | Primary personas | Integrated SDM capabilities (MVP) | Waves / notes |
|---|---|---|---|
| **SDM PM Console** | Project Manager, Delivery lead | Property readiness & wave gates, incident/FN roll-up for RAID, milestone exports | W1–16 registry; properties + incidents + field notices |
| **Service Delivery Console** | Service Delivery Manager, Engineer | Incidents, TAC, devices, assurance, WebEx bridges, sync health | W1,2,4 + ops KPIs; sources admin |
| **Success Console** | Customer Experience Manager, CSM/TAM | Adoption bars, health narratives, advisory/FN customer story | W5–16 context; properties + PSIRT + FN |
| **Renewals Console** | CXM, SAM/account team | License compliance, EoX/contract signals, inventory for renewals | W3, W4, W10; Smart Licensing + Support API + CSPC |

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
| **Add members** | Add delivery manager, TAC engineer, MGM IT manager, assigned engineer to space |
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

## MVP extended integration waves (5–15)

Mirrors [MVP_SCOPE_FREEZE.md](MVP_SCOPE_FREEZE.md). Env keys and endpoints are **placeholders** until Cisco API Console apps and docs are bound per tenant.

| Wave | Source | Typical API / access | Primary signal to platform | Notes |
|---|---|---|---|---|
| 5 | **ThousandEyes** | ThousandEyes REST API (tests, alerts, metrics) | Synthetic path outages, app/network correlation | Map tests to `properties` / services; feed `sla_metrics`, incident enrichment |
| 6 | **Cisco Umbrella** | Umbrella Reporting / Investigate APIs | DNS policy hits, blocked domains, roaming clients | Security and guest / WAN incident context |
| 7 | **Stealthwatch** | Cisco Secure Network Analytics API | Flow / anomaly / security events | Ties to `incidents`, `devices` (IP/flow correlation) |
| 8 | **DWDM** | Optical line system APIs or SNMP/telemetry collector (vendor-specific) | Span loss, alarms, channel health | Only where MGM runs managed optical; normalize into device or health entities |
| 9 | **Cisco IQ** | Product-specific analytics API (per entitlement and SKU naming) | Insights / recommendations | Bind to `property_technology_adoption`, reporting |
| 10 | **CSPC** | On‑prem collection platform to Cisco (collector / upload APIs as deployed) | Inventory and usage uploads | Complements SWAPI; validate against `cisco.licenses` / inventory |
| 11 | **Cisco ISE** | ISE ERS / OpenAPI, **ISE as Code** APIs (pxGrid where used) | Identity, profiling, posture, auth events; policy/object automation and config lifecycle | User/session context for incidents; reproducible ISE policy baselines and change visibility per MGM standards |
| 12 | **Cisco Spaces** | Spaces API (location, BLE/Wi‑Fi where deployed) | Maps, occupancy, visitor analytics | Property-level overlays |
| 13 | **Cisco Secure Access** | Secure Access / SSE APIs | ZTNA posture, tunnel status, app connectivity | Remote access incident diagnostics |
| 14 | **PSIRT / openVuln** | Cisco OpenVuln API (OAuth 2.0) — security advisories, CVE metadata | Exposure vs inventory (`model`, `software_version`, serial/PID); incident and property risk context | Align with [Cisco PSIRT openVuln](https://developer.cisco.com/docs/psirt) patterns; normalize advisory + CVE entities |
| 15 | **Cisco Field Notices** | Support / Field Notice APIs or published FN feeds | PID, serial, software ranges; workarounds and remediation | Match FNs to `mgm.devices` and properties; optional links to `mgm.incidents` for proactive tickets |

Suggested env placeholders (names only — no secrets in repo):

| Prefix | Purpose |
|---|---|
| `THOUSANDEYES_*` | API token, account/org IDs |
| `UMBRELLA_*` | API keys, org ID |
| `STEALTHWATCH_*` or `SNA_*` | host, API credential |
| `DWDM_*` | collector base URL or EMS endpoint |
| `CISCO_IQ_*` | service URL, OAuth or API key |
| `CSPC_*` | collector host, registration credentials |
| `ISE_*` | ERS / OpenAPI base URL, credentials, optional pxGrid; **ISE as Code** entitlement paths (export/import, automation APIs) per tenant |
| `CISCO_SPACES_*` | OAuth / API key per tenant |
| `SECURE_ACCESS_*` | SSE tenant URL, client credentials |
| `OPENVULN_*` | OAuth client id/secret, token URL, optional advisory scope |
| `FIELD_NOTICE_*` or `CISCO_FN_*` | API base URL, credentials or Support API reuse, polling schedule hints |

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
| 7 | **ThousandEyes** | ThousandEyes APIs | API token | MVP wave 5 (config) | `mgm.sla_metrics`, incident context |
| 8 | **Cisco Umbrella** | Umbrella APIs | API key / OAuth per product | MVP wave 6 (config) | Security / DNS context |
| 9 | **Stealthwatch (SNA)** | Secure Network Analytics API | API creds | MVP wave 7 (config) | Flow / security events |
| 10 | **DWDM / optical** | EMS / collector | varies | MVP wave 8 (config) | Optical health |
| 11 | **Cisco IQ** | Analytics APIs | OAuth / API key | MVP wave 9 (config) | Adoption / insights |
| 12 | **CSPC** | Collector platform | registration creds | MVP wave 10 (config) | Upload / inventory |
| 13 | **Cisco ISE** | ERS / OpenAPI / pxGrid / ISE as Code | admin / client | MVP wave 11 (config) | Identity posture; policy automation & config drift context |
| 14 | **Cisco Spaces** | Spaces API | OAuth / API key | MVP wave 12 (config) | Location / occupancy |
| 15 | **Cisco Secure Access** | SSE APIs | OAuth / token | MVP wave 13 (config) | ZTNA posture |
| 16 | **PSIRT / openVuln** | OpenVuln API — advisories & CVEs | OAuth 2.0 client | MVP wave 14 (config) | Vulnerability exposure vs inventory; security advisories |
| 17 | **Cisco Field Notices** | Support / FN APIs or feeds | API key / OAuth | MVP wave 15 (config) | PID/serial/software impact; proactive property/incident context |

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
    │           Service Delivery Manager backend (Node.js/Express)           │
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
| **PSIRT/openVuln + Field Notice implementation** | Waves 14–15 scoped; dedicated tables, sync jobs, and matchers not yet in schema | Advisory/CVE and FN data must be ingested and joined to `mgm.devices` / properties per OpenVuln and FN contracts |
| **No Meraki integration** | If any MGM properties use Meraki (common in hospitality), the design is pure DNA Center | Would miss a significant device population |
| **ThousandEyes in MVP waves** | ThousandEyes now in scope (Wave 5); wire env + API mapping | Still need concrete test-to-property mapping and alert sync |
| **AppDynamics** | Not in Waves 5–15; optional later | APM traces not auto-correlated unless added |
| **Phases 4–8 missing** | Integration layer (Phase 6) was not included in the document | The actual API client code, polling logic, error handling, and retry patterns are undefined |

---

*Generated from design analysis on 2026-04-03.*
