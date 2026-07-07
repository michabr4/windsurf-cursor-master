# Mimir API Integration Plan — Helix / Service Delivery Manager
## Wave 18

---

## 1. What Is Mimir?

Cisco Mimir is an internal **API Gateway and Runtime Platform** that exposes a unified REST interface over dozens of Cisco back-end data systems. Its key capabilities relevant to Helix are:

| Capability | Description |
|---|---|
| Network Profiler (NP) | Device inventory, hardware/SW lifecycle, PSIRT & Field Notice roll-ups, compliance (Best Practices), KPIs |
| Compliance (COMPLIANCE) | BP summary/detail, compliance track status |
| COLD | Product families, field-notice bulletins, PSIRT advisories, HW/SW EoX lookup |
| Business Critical Insights (BCIAPI) | Risk mitigation summary/detail, syslog statistics |
| BCI Benchmarking (BCIBM) | Peer-comparison data (PSIRT count, FN count, inventory, SW conformance) |
| Quarterly Business Review (QBR) | Composite lifecycle/PSIRT/FN/risk scores |
| Product Alerts | FN bulletins, HW EoL bulletins, security advisories |
| SORA | Software release recommendations |
| LOKI | Network topology modeling |
| INVENTORY | Device/interface/IP inventory |

**Base URI:** `https://mimir-prod.cisco.com/api/mimir/{service}/{request}`  
**Swagger UI:** `https://mimir-prod.cisco.com/swagger-ui/index.html`

---

## 2. Authentication Strategy

Mimir supports two mechanisms:

| Method | Use case |
|---|---|
| HTTP Basic (`Authorization: Basic base64(user:pass)`) | Quick prototyping / dev |
| **OAuth2 `client_credentials`** | **Production / M2M — preferred** |

For Helix, use **OAuth2 client_credentials** — this aligns with the existing `SMART_LICENSING` pattern already in `config.ts`.

New environment variables required (add to `.env.example` and `EnvSchema`):

```
MIMIR_BASE_URL=https://mimir-prod.cisco.com/api/mimir
MIMIR_OAUTH_TOKEN_URL=https://cloudsso.cisco.com/as/token.oauth2
MIMIR_CLIENT_ID=
MIMIR_CLIENT_SECRET=
```

> **Security note (codeguard-1-hardcoded-credentials):** Credentials must never be hardcoded. Store via `.env` / secrets manager only. `MIMIR_CLIENT_ID` and `MIMIR_CLIENT_SECRET` default to empty string in dev exactly as `SMART_LICENSING_CLIENT_ID/SECRET` do today.

---

## 3. Data Mapping — Mimir Services → Helix UI Views

### 3.1 `#devices` — Device Inventory View
**Current state:** DNA Center devices, Meraki data  
**Mimir additions:**

| Mimir Endpoint | Data | Widget |
|---|---|---|
| `GET /np/devices` | Device name, IP, product ID, SW version, role | Augment existing device table with Mimir columns |
| `GET /np/hardware` | Chassis details, HW EoS/EoL dates | HW lifecycle badge on each device row |
| `GET /np/software` | SW version, conformance status, EoS dates | SW lifecycle badge |
| `GET /np/kpi-hw-eox` | Summary counts: EoS/EoL devices | KPI card: "HW Lifecycle Risk" |
| `GET /np/kpi-sw-eox` | Summary counts: SW EoS/EoL | KPI card: "SW Lifecycle Risk" |
| `GET /inventory` | Interface + IP address details | Expandable device detail panel |

### 3.2 `#security` — Security / PSIRT View
**Current state:** PSIRT/OpenVuln data (Wave 14)  
**Mimir additions:**

| Mimir Endpoint | Data | Widget |
|---|---|---|
| `GET /np/psirt-summary` | Total PSIRT count, critical/high/med/low buckets | Replace or augment existing PSIRT KPI cards |
| `GET /np/psirt-details` | Per-device advisory list | Drill-down table |
| `GET /np/kpi-psirt` | Customer PSIRT exposure score | Gauge / trend sparkline |
| `GET /cold/psirt-bulletins` | Latest advisory bulletins | Advisory bulletin feed |
| `GET /product-alerts/security-advisory-bulletins` | Active security advisories | Alert banner |
| `GET /bcibm/psirt-count-peer-comparison` | Customer vs. peer PSIRT exposure | Peer comparison bar chart |
| `GET /bciapi/risk-mitigation-summary` | Overall risk mitigation score | Risk score card |

### 3.3 `#fieldnotes` — Field Notices View
**Current state:** Field Notices (Wave 15)  
**Mimir additions:**

| Mimir Endpoint | Data | Widget |
|---|---|---|
| `GET /np/fn-summary` | FN count, affected device count | Augment existing FN KPI banner |
| `GET /np/fn-details` | Per-device FN list | Drill-down table (replaces/augments W15 table) |
| `GET /cold/field-notices` | Full FN catalog for product IDs | FN detail panel |
| `GET /product-alerts/field-notice-bulletins` | Latest FN bulletin feed | Bulletin list |
| `GET /bcibm/fn-count-peer-comparison` | Customer vs. peer FN exposure | Peer comparison bar chart |

### 3.4 `#overview` — Overview / KPI Dashboard
**Current state:** Incident counts, device summary, TAC cases  
**Mimir additions:**

| Mimir Endpoint | Data | Widget |
|---|---|---|
| `GET /qbr/risk-composite` | Composite risk score (PSIRT + FN + lifecycle) | QBR Risk Score tile |
| `GET /qbr/psirt` | PSIRT composite score trend | Mini sparkline |
| `GET /qbr/field-notice` | FN composite score trend | Mini sparkline |
| `GET /qbr/lifecycle-hardware` | HW lifecycle score | Lifecycle gauge |
| `GET /qbr/lifecycle-software` | SW lifecycle score | Lifecycle gauge |
| `GET /bciapi/risk-mitigation-summary` | Actionable risk mitigation items count | "Action Required" KPI card |

### 3.5 `#integrations` — Waves & Integrations View
Register Mimir as **Wave 18** in the wave registry:

```
Wave 18 — Cisco Mimir API
  Services: NP, COMPLIANCE, COLD, BCIAPI, BCIBM, QBR, PRODUCT-ALERTS, SORA
  Auth: OAuth2 client_credentials
  Status: [configured / unconfigured based on env vars]
```

### 3.6 `#sources` — Source Administration
Add Mimir source config card showing:
- Connection status (live token check)
- `client_id` label (masked)
- Last sync timestamp
- Manual "Sync Now" trigger button → `POST /api/v1/integrations/sync/mimir`

---

## 4. Backend Implementation Plan

### 4.1 New File: `backend/src/integrations/mimirClient.ts`

Responsibilities:
- OAuth2 token acquisition and in-memory caching with expiry (same pattern as `smartLicensingClient.ts`)
- Typed response interfaces for each Mimir resource
- Named methods per resource (e.g. `getNpDevices()`, `getPsirtSummary()`, `getQbrComposite()`)
- Graceful empty-array returns on auth failures or network errors (same pattern as `tacClient.ts`)

```typescript
export class MimirClient {
  private tokenCache: { token: string; expiresAt: number } | null = null;

  constructor(
    private readonly baseUrl: string,
    private readonly tokenUrl: string,
    private readonly clientId: string,
    private readonly clientSecret: string
  ) {}

  private async getAccessToken(): Promise<string> { /* ... */ }
  async getNpDevices(companyId: string): Promise<MimirDevice[]> { /* ... */ }
  async getPsirtSummary(companyId: string): Promise<MimirPsirtSummary | null> { /* ... */ }
  async getFnSummary(companyId: string): Promise<MimirFnSummary | null> { /* ... */ }
  async getQbrComposite(companyId: string): Promise<MimirQbrComposite | null> { /* ... */ }
  async getBcibmPeerComparison(companyId: string): Promise<MimirBenchmark | null> { /* ... */ }
}
```

### 4.2 New File: `backend/src/routes/mimir.ts`

Express router mounted at `/api/v1/mimir`:

| Route | Method | Description |
|---|---|---|
| `/devices` | GET | NP device list |
| `/psirt-summary` | GET | PSIRT summary for company |
| `/psirt-details` | GET | Per-device PSIRT detail |
| `/fn-summary` | GET | Field notice summary |
| `/fn-details` | GET | Per-device FN detail |
| `/compliance-bp` | GET | BP summary/detail |
| `/qbr` | GET | QBR composite scores |
| `/peer-comparison` | GET | BCIBM peer benchmarks |
| `/risk-summary` | GET | BCIAPI risk mitigation |

All routes require `requireAuth`. Read operations accessible to `viewer` role and above.

### 4.3 `backend/src/config.ts` — Add Mimir env vars

```typescript
MIMIR_BASE_URL: z.string().default("https://mimir-prod.cisco.com/api/mimir"),
MIMIR_OAUTH_TOKEN_URL: z.string().default("https://cloudsso.cisco.com/as/token.oauth2"),
MIMIR_CLIENT_ID: z.string().default(""),
MIMIR_CLIENT_SECRET: z.string().default(""),
```

### 4.4 `backend/src/routes/integrations.ts` — Add `mimir` source

Add `"mimir"` to `SyncSourceParamSchema` and a `runMimirSync()` handler that calls `mimirClient` and upserts snapshot records.

### 4.5 Database Migrations

New tables under `cisco` schema:

```sql
CREATE TABLE IF NOT EXISTS cisco.mimir_inventory_snapshot (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  synced_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  company_id   TEXT NOT NULL,
  device_name  TEXT,
  product_id   TEXT,
  sw_version   TEXT,
  hw_eol_date  DATE,
  sw_eos_date  DATE,
  raw_json     JSONB
);

CREATE TABLE IF NOT EXISTS cisco.mimir_psirt_snapshot (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  synced_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  company_id   TEXT NOT NULL,
  total_count  INT,
  critical     INT,
  high         INT,
  medium       INT,
  low          INT,
  raw_json     JSONB
);

CREATE TABLE IF NOT EXISTS cisco.mimir_fn_snapshot (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  synced_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  company_id   TEXT NOT NULL,
  total_count  INT,
  affected_devices INT,
  raw_json     JSONB
);

CREATE TABLE IF NOT EXISTS cisco.mimir_qbr_snapshot (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  synced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  company_id          TEXT NOT NULL,
  risk_composite      NUMERIC,
  psirt_score         NUMERIC,
  fn_score            NUMERIC,
  hw_lifecycle_score  NUMERIC,
  sw_lifecycle_score  NUMERIC,
  raw_json            JSONB
);
```

---

## 5. Mockup Hub Updates (`backend/public/mockup/`)

The static mockup hub (`mockup-hub.js`) needs:

1. **Wave registry** — add Wave 18 entry:
   ```js
   { wave: 18, name: "Cisco Mimir API", status: "planned",
     services: ["NP","COMPLIANCE","COLD","BCIAPI","BCIBM","QBR","PRODUCT-ALERTS"] }
   ```
2. **`#devices` view** — add "Mimir Network Profile" tab/card with placeholder device table
3. **`#security` view** — add "Mimir PSIRT" KPI cards and peer-comparison panel placeholder
4. **`#fieldnotes` view** — add "Mimir Field Notices" count banner
5. **`#overview` view** — add QBR composite score tiles row
6. **`#sources` view** — add Mimir source config card

---

## 6. Phased Delivery

| Phase | Deliverables | Priority |
|---|---|---|
| **P1 — Client + Auth** | `mimirClient.ts`, env vars in `config.ts`, `.env.example` update | High |
| **P2 — Core Routes** | `routes/mimir.ts` (devices, PSIRT, FN), sync source registration | High |
| **P3 — DB Snapshots** | Migration for 4 snapshot tables, sync job writes snapshots | Medium |
| **P4 — UI: Security + FN** | `#security` + `#fieldnotes` Mimir widgets | Medium |
| **P5 — UI: Devices + Overview** | `#devices` Mimir columns, `#overview` QBR tiles | Medium |
| **P6 — UI: Peer Comparison** | BCIBM charts, `#integrations` Wave 18, `#sources` card | Low |
| **P7 — Mockup Hub** | Mockup widget stubs for all above | Low |

---

## 7. Open Questions / Prerequisites

- [ ] Obtain Mimir OAuth2 `client_id` + `client_secret` from Cisco CX/IT team
- [ ] Confirm the correct `company_id` parameter format for MGM GES-West (Mimir uses a customer/company scoping param on most NP endpoints)
- [ ] Confirm token endpoint URL — likely `https://cloudsso.cisco.com/as/token.oauth2` (same as Smart Licensing) but may differ for Mimir-specific OAuth apps
- [ ] Verify Mimir network reachability from Helix deployment host (VPN/proxy may be required)
- [ ] Determine desired sync cadence (suggestion: PSIRT/FN every 4h via cron, devices every 24h)

---

## 8. File Touch List (Implementation)

```
platforms/serviceflow-sdm/
  .env.example                                     ← add MIMIR_* vars
  backend/src/config.ts                            ← add 4 MIMIR env entries to EnvSchema
  backend/src/integrations/mimirClient.ts          ← NEW
  backend/src/routes/mimir.ts                      ← NEW
  backend/src/app.ts                               ← mount mimirRouter
  backend/src/routes/integrations.ts              ← add "mimir" to SyncSourceParamSchema
  backend/src/jobs/syncService.ts                  ← add runMimirSync()
  backend/src/schemas/integrations.ts              ← extend source enum
  backend/migrations/XXXX_mimir_snapshots.sql      ← NEW
  backend/public/mockup/mockup-hub.js              ← Wave 18 + widget stubs
  docs/MIMIR_INTEGRATION_PLAN.md                   ← THIS FILE
```
