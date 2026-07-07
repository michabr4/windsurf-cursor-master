# Service Delivery Manager — MVP Scope Freeze

## Objective
Deliver a functional MVP for MGM service delivery operations with incident management, device visibility, and TAC-linked workflows, with **integrated capabilities aligned to Cisco and partner operational consoles** used in service delivery (API-backed; no console UI scraping).

## In Scope
- Authentication and role-based access control for:
  - `admin`, `sdm`, `tam`, `csm`, `engineer`, `manager`, `viewer`
- Core data domains:
  - Properties
  - Devices
  - Incidents and incident updates
  - TAC case linkage metadata
  - Operational dashboard summary metrics
- External integration waves:
  - Wave 1: DNA Center
  - Wave 2: TAC API
  - Wave 3: Smart Licensing
  - Wave 4: WebEx and Support API enrichment
  - Wave 5: ThousandEyes (synthetic paths, tests, and correlated app outages)
  - Wave 6: Cisco Umbrella (DNS and secure internet gateway signals)
  - Wave 7: Cisco Secure Network Analytics (Stealthwatch) — flow and security analytics
  - Wave 8: DWDM / optical transport telemetry (aligned to deployed optical line systems)
  - Wave 9: Cisco IQ (insights / analytics APIs per entitlement and product naming)
  - Wave 10: CSPC (Cisco platform / collector — scope per smart-account and on-prem deployment)
  - Wave 11: Cisco ISE — runtime context **and ISE as Code** (identity, posture, profiling, pxGrid/session signals where used; API-driven policy and configuration automation, export/import and declarative workflows aligned to Cisco ISE as Code)
  - Wave 12: Cisco Spaces (location, occupancy, and digital experience where deployed)
  - Wave 13: Cisco Secure Access (SSE / ZTNA posture and connectivity signals)
  - Wave 14: PSIRT / openVuln-aligned feeds (Cisco security advisories, CVE metadata, and vulnerability exposure correlation against device inventory and software versions)
  - Wave 15: Cisco Field Notices (FN) — ingest, match to PIDs / serials / software in inventory, and surface proactive impact on properties and incidents
  - Wave 16: Cisco Firepower Management Center (FMC) — FTD / managed-device inventory, access control policies, and network/host objects via published FMC REST APIs (console parity for core read/act patterns used in service delivery)
- **Vendor console capability coverage (MVP):** For each entitled integration wave, **Service Delivery Manager** implements **capability parity with the corresponding operational console(s)** through documented APIs, so delivery-manager / TAM / engineer workflows do not depend on manual swivel-chair across vendor UIs for core read–act patterns (inventory, health, licensing, security context, collaboration, advisories, field notices). Mapped coverage:
  - **Cisco API Console (DevNet):** Client apps, OAuth/API keys, and contract-scoped API products that **gate** Waves 1–16; entitlement verification and credential lifecycle treated as a first-class prerequisite in onboarding.
  - **Cisco Catalyst Center** (Wave 1): Inventory, sites, device health, assurance/issues, diagnostics.
  - **Cisco Smart Software Manager / Smart Licensing–class portals** (Wave 3): Smart Account / Virtual Account alignment, entitlements, consumption, compliance signals.
  - **Cisco Support / TAC & Case Management** (Waves 2, 4): Service request lifecycle, case detail, contract/EoX/Bug enrichment where APIs exist.
  - **WebEx Control Hub–class collaboration** (Wave 4): Spaces, meetings, and incident-linked war-room patterns via WebEx APIs.
  - **ThousandEyes** (Wave 5): Tests, alerts, paths — parity with org-level visibility relevant to service delivery.
  - **Cisco Umbrella** (Wave 6): Reporting / policy / investigate-class signals as entitled.
  - **Cisco Secure Network Analytics (Stealthwatch)** (Wave 7): Flow/security analytics console–class context for triage.
  - **Optical / DWDM EMS or equivalent** (Wave 8): Transport health where MGM operates managed optical.
  - **Cisco IQ** (Wave 9): Insights and analytics surfaces per entitlement.
  - **CSPC / collector deployment** (Wave 10): Collection and upload alignment with inventory and Smart Account expectations.
  - **Cisco ISE Administration + ISE as Code** (Wave 11): Identity, posture, profiling, policy/config automation.
  - **Cisco Spaces** (Wave 12): Location, occupancy, and digital experience where deployed.
  - **Cisco Secure Access** (Wave 13): SSE/ZTNA posture and connectivity diagnostics.
  - **PSIRT / OpenVuln & security advisory interfaces** (Wave 14): Advisory and CVE exposure vs inventory.
  - **Cisco Field Notice channels** (Wave 15): FN impact on PIDs, serials, and software in estate.
  - **Cisco Firepower Management Center** (Wave 16): FTD inventory, access policies, objects — FMC REST API parity for security delivery workflows alongside DNA and ISE context.
  - **Salesforce CRM** (Wave 17): Full Salesforce REST API v59.0 integration via OAuth 2.0 connected app. Objects: Cases, Accounts, Contacts, Opportunities, Entitlements, Service Contracts, Tasks, Knowledge Articles. Feeds all six SDC program consoles — Cases → Service Delivery, Opportunities → Renewals, Entitlements → Success, Accounts → PM + High Touch. Backend routes at `/api/v1/salesforce/*` with RBAC-gated access, token caching (~110 min TTL), parameterized SOQL queries. Console summary endpoint aggregates pipeline, case, and entitlement metrics for the Experience Command view.
  - **SDC program & delivery consoles (persona-aligned, API-backed in SDM):** Key workflows from Cisco **Service Delivery Cloud (SDC)**-class consoles are **integrated into Service Delivery Manager** so Project Managers, Service Delivery Managers, Customer Experience Managers, Customer Delivery Architects, and **Engineers** (technical delivery) do not swivel-chair for core read/act patterns:
    - **SDM PM Console (Project Manager):** Program milestones, wave/readiness tracking per property, RAID-style roll-up (incidents + field notices + EoX), stakeholder status exports — surfaced via **properties**, **incidents**, **integrations** registry, **field notices**, and **overview** KPIs.
    - **Service Delivery Console (Service Delivery Manager):** Operational command — incident queue, **TAC** linkage, device inventory and assurance (including **FMC**/FTD where entitled), **WebEx** war-room hooks, integration sync health — primary **SDM** shell (**incidents**, **devices**, **sources**, **waves**).
    - **Success Console (Customer Experience Manager):** Adoption and health narratives per property, success milestones vs enabled waves, customer-visible risk posture (**PSIRT** / **FN** / licensing story) — **properties**, **overview**, **security**, **field notices**, **integrations**.
    - **Renewals Console (CXM / lifecycle):** **Smart Licensing** (Wave 3) compliance and consumption, **Support API** contract/EoX enrichment (Wave 4), renewal-risk context tied to inventory and **CSPC** (Wave 10) — **overview** licensing KPIs, **devices**, **integrations**.
  - **Meraki Dashboard** (in-scope — merged into Devices, Properties, and Waves views): Cloud-managed networking visibility via Meraki Dashboard API v1 — networks, devices, clients, alerts, and config templates across MR/MS/MX/MV product lines. Data surfaces inline on Devices (inventory), Properties (per-site mapping), and Waves & Integrations (DD-K wave). Combined with **Meraki as Code** (SaC Wave E) for automated configuration.
  - **Cisco AppDynamics** (in-scope — merged into Devices, Incidents, and Overview views): Application Performance Monitoring (APM) — application health, business transactions, infrastructure nodes. Data surfaces inline on Devices (infra ↔ app mapping), Incidents (health-rule violation correlation), and Overview (automation pulse). DD-L wave in Waves & Integrations.
- **Digitized Delivery** — a new program section covering automation-driven service delivery:
  - **Network as Code (NaC):** Cisco NaC framework applying IaC and DevOps to network management. Solutions: Catalyst Center NaC, SD-WAN NaC, ISE NaC, IOS-XE NaC, plus NaC toolchain (nac-collector, nac-test, nac-validate, nac-tool, nac-api). Maps customer estate to automation readiness scores. Source: [netascode.cisco.com](https://netascode.cisco.com/).
  - **Services as Code (SaC):** Cisco SaC framework — defines network infrastructure state as versioned code. Development waves: ACI as Code (Wave A), SD-WAN as Code (B), NDFC as Code (C), ISE as Code (D), Meraki as Code (E), Catalyst Center as Code (F), Unified Branch as Code (G), FMC as Code (H), IOS-XE as Code (I), IOS-XR as Code (J), SaC AI Assistant, and DDS. Includes partner co-delivery route-to-market. Automation environments: Ansible, Terraform, CI/CD pipelines. Available as Cisco Professional Services annual subscription. Source: [Cisco SaC Portal](https://cisco.sharepoint.com/sites/service-as-code).
  - **Digital Document Solutions (DDS):** Digitized delivery document lifecycle — automated generation from SDM data, multi-stakeholder approval workflows, secure customer-facing sharing with expiry, version control, and template library (Network Assessment, Automation Readiness, Incident Summary, QBR Pack, Security Posture, Wave Runbook). API-driven (`/api/v1/dds/*`).
- Audit event logging for security-sensitive operations.

## Out of Scope (MVP)
- Advanced reporting exports beyond basic JSON/CSV.
- Mobile-native app release.
- Multi-region/high-availability production topology.

## Functional Milestones
1. Repo/bootstrap + local runtime.
2. Migration-driven DB + seed.
3. Backend APIs for auth/properties/devices/incidents.
4. Frontend shell and operational pages.
5. DNA Center + TAC ingestion.
6. Rollout of Waves 5–16 per API entitlement, data contracts, and MGM property coverage (including PSIRT/openVuln, Field Notices correlation, **ISE as Code** under Wave 11, **FMC** under Wave 16, and **vendor console–aligned capabilities** per mapping above).
7. **Meraki + AppDynamics data merge** — Meraki inventory and AppDynamics APM data integrated inline across Devices, Properties, Incidents, and Overview views (no standalone pages).
8. **Digitized Delivery** — Network as Code estate assessment + ROI calculator, Services as Code wave deployment (A–J + DDS) + ROI calculator, AI Assistant enablement, partner co-delivery setup, DDS template library, and per-role automation strategy recommendations.
9. **DD waves in Integrations** — 14 Digitized Delivery waves (DD-A through DD-N) added to Waves & Integrations registry with API, Terraform, Ansible, and AI Assistant capability matrix.
10. **Salesforce CRM integration (Wave 17)** — OAuth 2.0 connected app, Salesforce REST API v59.0, SOQL parameterized queries, token caching. Backend routes for Cases, Accounts, Contacts, Opportunities, Entitlements, Service Contracts, Tasks, and Knowledge Articles. Console summary endpoint for Experience Command. Frontend Salesforce page with tabs and KPIs. Salesforce data panels wired into all six SDC program consoles: PM (accounts + pipeline), Service Delivery (case correlation), Success (entitlements + account health), Renewals (opportunities + service contracts), Delivery Architect (knowledge articles + accounts), High Touch Operations (executive CRM pulse). AI insights for Salesforce on overview, sdcroles, and incidents views.
11. QA pass and deployment readiness runbook.

## Definition of Done (MVP)
- Local stack runs with `docker compose up`.
- User can log in and perform role-permitted actions.
- User can create/update incidents and view timeline updates.
- Incidents can be linked to TAC data.
- Device inventory is populated from at least one integration flow.
- Test suite and lint/type checks pass in CI.
- For each **enabled** integration, operators can complete **console-equivalent core tasks** from **Service Delivery Manager** within the scope of published APIs (inventory/health, licensing visibility, TAC linkage, collaboration hooks, and security/FN context as applicable).
- **Meraki Dashboard** data is visible inline on Devices (cloud-managed inventory), Properties (per-site DD readiness), and Waves (DD-K wave).
- **AppDynamics** data is visible inline on Devices (infra ↔ app mapping), Incidents (health-rule correlation), and Overview (automation pulse).
- **Digitized Delivery** surfaces (NaC, SaC, DDS) are accessible in the hub with ROI calculators, per-role automation strategies, and magenta-accented callouts. DD waves (DD-A through DD-N) populate in Waves & Integrations.
- **Splunk magenta callouts** on all views referencing Digitized Delivery positioning and next steps. AI insights use magenta accent for DD-specific recommendations.
- **Salesforce CRM** data powers all SDC consoles: Cases correlate with incidents (Service Delivery), Opportunities feed the Renewals pipeline, Entitlements drive Success health scores, Accounts populate PM and High Touch dashboards. Wave 17 row in Integrations registry. Console summary aggregates CRM metrics into Experience Command.
