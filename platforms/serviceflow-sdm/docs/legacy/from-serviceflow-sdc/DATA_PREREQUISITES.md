# Service Delivery Manager — Defined Data Prerequisites

> Extracted from: `CLAUDE_md - Service Delivery Manager Application Development Guide.msg`
> Source: Michael Brown (SDM, Cisco CX) via Circuit / Claude Sonnet 4.5
> Analysis date: 2026-04-03

---

## 1. Document Summary

| Field | Value |
|---|---|
| Application | Service Delivery Manager |
| Customer | MGM Resorts International (GES-West) |
| Platforms | Web, Mobile (iOS/Android), Desktop |
| Backend | Node.js 20.x, TypeScript, Express |
| Frontend | React 18, TypeScript, Material-UI |
| Database | PostgreSQL 15, Redis 7 |
| Mobile | React Native |
| Key Integrations | MS Teams, WebEx, Cisco TAC, DNA Center, Smart Licensing |
| Phases defined | 8 (Environment → Deployment) |
| Guide completeness | Phases 1–3 are fully specified; Phases 4–8 are referenced in the TOC but **not included** in the extracted body |

---

## 2. Infrastructure Prerequisites

### 2.1 System Requirements
| Requirement | Minimum |
|---|---|
| OS | Ubuntu 22.04+, macOS 12+, or Windows WSL2 |
| RAM | 16 GB |
| Storage | 50 GB free |
| Internet | Stable connection |

### 2.2 Core Software Dependencies
| Component | Version | Purpose |
|---|---|---|
| Node.js | 20.x LTS | Runtime |
| npm | 10.x | Package manager |
| PostgreSQL | 15 | Primary RDBMS |
| Redis | 7 (alpine) | Cache / session store / job queues |
| Docker | latest | Containerisation |
| Docker Compose | latest | Multi-container orchestration |
| Git | latest | Version control |
| Python 3 + pip | latest | Build tools |

---

## 3. Database Prerequisites

### 3.1 PostgreSQL Setup
| Item | Value |
|---|---|
| Database name | `serviceflow_sdm` |
| Admin user | `serviceflow_admin` |
| Extensions required | `uuid-ossp`, `pg_trgm`, `pgcrypto` |
| Schemas | `mgm` (core), `cisco` (Cisco-specific), `audit` (logging) |

### 3.2 Complete Table Inventory (20 tables)

#### Schema: `mgm` (13 tables)
| Table | Purpose | Key Foreign Keys |
|---|---|---|
| `users` | Auth & user profiles | — |
| `properties` | MGM resort locations | `users.user_id` (IT manager) |
| `devices` | Network infrastructure | `properties.property_id` |
| `incidents` | Service incidents | `properties`, `devices`, `users` (reported_by, assigned_to), self-ref (parent) |
| `incident_updates` | Incident history | `incidents`, `users` |
| `property_technology_adoption` | Tech adoption per property | `properties`, `cisco.technologies`, `users` |
| `adoption_history` | Adoption time-series | `property_technology_adoption` |
| `property_license_usage` | License consumption per property | `cisco.licenses`, `properties` |
| `sla_metrics` | SLA KPIs (daily/weekly/monthly/quarterly/annual) | `properties` |
| `changes` | RFC / change management | `properties`, `users` (4 roles), self-ref (parent) |
| `teams_channels` | MS Teams integration | `properties`, `incidents`, `users` |
| `webex_spaces` | WebEx integration | `properties`, `incidents`, `cisco.tac_cases` |
| `notifications` | User notifications | `users` |
| `dashboards` | User dashboard configs | `users` |
| `reports` | Report definitions | `users` |
| `report_history` | Report generation log | `reports`, `users` |

#### Schema: `cisco` (5 tables)
| Table | Purpose | Key Foreign Keys |
|---|---|---|
| `tac_cases` | Cisco TAC support cases | `mgm.incidents`, `mgm.properties`, `mgm.devices`, `mgm.users` |
| `tac_case_updates` | TAC case history | `tac_cases` |
| `technologies` | Technology portfolio | `mgm.users` (PM, tech lead) |
| `licenses` | License/subscription tracking | `mgm.users` (owner) |
| `license_history` | License event log | `licenses`, `mgm.users` |

#### Schema: `audit` (1 table)
| Table | Purpose |
|---|---|
| `activity_log` | Full CRUD audit trail with IP, user-agent, old/new values |

### 3.3 Auto-Generated Sequences & Triggers
| Trigger | Target | Behavior |
|---|---|---|
| `generate_incident_number` | `mgm.incidents` | Auto-generates `INC-000001` pattern |
| `generate_change_number` | `mgm.changes` | Auto-generates `CHG-000001` pattern |
| `calculate_resolution_time` | `mgm.incidents` | Computes `resolution_time` on resolve |
| `update_*_updated_at` (×11) | All major tables | Sets `updated_at` on UPDATE |

---

## 4. External Service / Credential Prerequisites

Every integration below requires credentials provisioned **before** the application can function.

### 4.1 Microsoft Teams
| Variable | Description |
|---|---|
| `TEAMS_CLIENT_ID` | Azure AD App Registration — Client ID |
| `TEAMS_CLIENT_SECRET` | Azure AD App Registration — Client Secret |
| `TEAMS_TENANT_ID` | Azure AD Tenant ID |
| `TEAMS_BOT_ID` | Teams Bot registration ID |
| `TEAMS_BOT_PASSWORD` | Teams Bot password |
| `TEAMS_WEBHOOK_BASE_URL` | Public callback URL |

**Prerequisite:** Azure AD App Registration with Microsoft Graph API permissions; Teams Bot registration.

### 4.2 Cisco WebEx
| Variable | Description |
|---|---|
| `WEBEX_CLIENT_ID` | WebEx Integration Client ID |
| `WEBEX_CLIENT_SECRET` | WebEx Integration Client Secret |
| `WEBEX_BOT_TOKEN` | WebEx Bot access token |
| `WEBEX_WEBHOOK_SECRET` | Webhook signature secret |
| `WEBEX_REDIRECT_URI` | OAuth callback URL |

**Prerequisite:** WebEx Developer App (Integration + Bot) registered at developer.webex.com.

### 4.3 Cisco TAC API
| Variable | Description |
|---|---|
| `TAC_API_KEY` | TAC API key |
| `TAC_API_SECRET` | TAC API secret |
| `TAC_BASE_URL` | `https://tools.cisco.com/tac/api/v2` |
| `TAC_CONTRACT_NUMBER` | `GES-W-2024-MGM` |

**Prerequisite:** Cisco API Console access; valid GES-West service contract with TAC API entitlement.

### 4.4 Cisco DNA Center
| Variable | Description |
|---|---|
| `DNA_CENTER_HOST` | DNAC hostname/IP |
| `DNA_CENTER_USERNAME` | API username |
| `DNA_CENTER_PASSWORD` | API password |
| `DNA_CENTER_PORT` | 443 |

**Prerequisite:** DNA Center instance deployed and accessible; API-enabled service account.

### 4.5 Cisco Smart Licensing
| Variable | Description |
|---|---|
| `SMART_LICENSING_CLIENT_ID` | Smart Account OAuth client ID |
| `SMART_LICENSING_CLIENT_SECRET` | Smart Account OAuth client secret |
| `SMART_LICENSING_TOKEN_URL` | `https://cloudsso.cisco.com/as/token.oauth2` |
| `SMART_LICENSING_API_URL` | `https://swapi.cisco.com/services/api/smart-accounts-and-licensing` |

**Prerequisite:** Cisco Smart Account with API access; OAuth client registration at apiconsole.cisco.com.

### 4.6 Email / SMTP
| Variable | Description |
|---|---|
| `SMTP_HOST` | e.g. `smtp.gmail.com` |
| `SMTP_PORT` | 587 |
| `SMTP_USER` | Sending email address |
| `SMTP_PASSWORD` | App password / SMTP credentials |
| `EMAIL_FROM` | `noreply@serviceflow-sdm.com` |

### 4.7 AWS (Production)
| Variable | Description |
|---|---|
| `AWS_REGION` | `us-west-2` |
| `AWS_ACCESS_KEY_ID` | IAM access key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key |
| `S3_BUCKET` | `serviceflow-sdm-uploads` |

**Prerequisite:** AWS account, IAM user with S3 permissions, bucket created.

---

## 5. Application Configuration Prerequisites

### 5.1 Security / JWT
| Variable | Requirement |
|---|---|
| `JWT_SECRET` | Min 32-char random string |
| `JWT_EXPIRE` | Default `24h` |
| `JWT_REFRESH_SECRET` | Min 32-char random string |
| `JWT_REFRESH_EXPIRE` | Default `7d` |
| `BCRYPT_ROUNDS` | Default `12` |

### 5.2 CORS
| Variable | Default |
|---|---|
| `CORS_ORIGIN` | `http://localhost:3001,http://localhost:3000` |

### 5.3 Rate Limiting
| Variable | Default |
|---|---|
| `RATE_LIMIT_WINDOW_MS` | 900000 (15 min) |
| `RATE_LIMIT_MAX_REQUESTS` | 100 |

### 5.4 WebSocket
| Variable | Default |
|---|---|
| `SOCKET_IO_PATH` | `/socket.io` |
| `SOCKET_IO_CORS` | `http://localhost:3001` |

### 5.5 Feature Flags
| Flag | Default |
|---|---|
| `ENABLE_TAC_AUTO_CREATE` | `true` |
| `ENABLE_TEAMS_INTEGRATION` | `true` |
| `ENABLE_WEBEX_INTEGRATION` | `true` |
| `ENABLE_EMAIL_NOTIFICATIONS` | `true` |

---

## 6. Docker / Containerisation Prerequisites

| Container | Image | Ports | Health Check |
|---|---|---|---|
| `serviceflow-postgres` | `postgres:15-alpine` | 5432 | `pg_isready` |
| `serviceflow-redis` | `redis:7-alpine` | 6379 | `redis-cli ping` |
| `serviceflow-backend` | Custom (Node 20 alpine) | 3000, 9229 (debug) | HTTP `/health` |
| `serviceflow-frontend` | Custom → nginx:alpine (prod) | 3001 (dev) / 80 (prod) | — |
| `serviceflow-pgadmin` | `dpage/pgadmin4:latest` | 5050 | — |

---

## 7. User Role Enumeration (Data Prerequisite)

The system defines 7 user roles that must be seeded or provisioned:

| Role | Description (inferred) |
|---|---|
| `admin` | System administrator |
| `sdm` | Service Delivery Manager |
| `tam` | Technical Account Manager |
| `csm` | Customer Success Manager |
| `engineer` | Network / support engineer |
| `manager` | People / operations manager |
| `viewer` | Read-only stakeholder |

---

## 8. Domain Enumerations (Constrained Values)

| Domain | Values |
|---|---|
| Property types | `hotel`, `casino`, `resort`, `venue` |
| Device statuses | `active`, `inactive`, `maintenance`, `decommissioned`, `failed` |
| Incident priorities | `P1`, `P2`, `P3`, `P4` |
| Incident statuses | `open`, `acknowledged`, `investigating`, `in-progress`, `pending`, `resolved`, `closed`, `cancelled` |
| TAC severities | `1`, `2`, `3`, `4` |
| TAC statuses | `open`, `in-progress`, `pending-customer`, `pending-cisco`, `resolved`, `closed` |
| Technology categories | `Network Infrastructure`, `Security`, `Wireless`, `Collaboration`, `Data Center`, `Observability`, `Cloud` |
| Deployment phases | `planning`, `design`, `pilot`, `deployment`, `production`, `complete` |
| Change types | `standard`, `normal`, `emergency`, `pre-approved` |
| Change risk levels | `low`, `medium`, `high`, `critical` |
| License models | `perpetual`, `subscription`, `term`, `consumption` |
| SLA metric types | `daily`, `weekly`, `monthly`, `quarterly`, `annual` |
| Notification types | `incident`, `tac_case`, `change`, `sla_breach`, `license_expiry`, `system`, `alert` |
| Report formats | `pdf`, `excel`, `csv`, `json` |

---

## 9. What Is Missing (Phases 4–8 Not in Document)

The extracted guide covers **Phases 1–3 only**. The following are referenced in the TOC but were not included in the `.msg` file body:

| Phase | Title | Status |
|---|---|---|
| Phase 4 | Backend API Development | NOT INCLUDED |
| Phase 5 | Frontend Development | NOT INCLUDED |
| Phase 6 | Integration Layer | NOT INCLUDED |
| Phase 7 | Testing & Quality Assurance | NOT INCLUDED |
| Phase 8 | Deployment | NOT INCLUDED |

These missing phases would define additional prerequisites around API route structures, frontend component data contracts, integration authentication flows, test data seeding, and production infrastructure (likely AWS ECS/EKS, RDS, ElastiCache, ALB, etc.).

---

*Generated from `.msg` extraction on 2026-04-03.*
