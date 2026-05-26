# Palo Alto to Cisco Secure Firewall  
# High-level migration plan (MGM) — *expectations, prerequisites, and timeline*

**Purpose of this document**  
Translate working technical action items and preliminary planning into a **single, calm narrative** for MGM leaders and extended teams. It is **not** a substitute for the formal *Requirements*, *Solution Design*, *MTO/MOP*, or the detailed schedule owned by the Cisco program manager. Those artifacts remain the system of record as they are finalized.

**What is changing (at a glance)**  
MGM is moving from **Palo Alto** to **Cisco Firepower Threat Defense (FTD)** on new appliances, with centralized management (**FMC** and/or **Cisco Security Cloud Control**, per final design). **Technologent** is expected to lead **physical** site work (site survey, rack, stack, cabling) in line with the commercial proposal. **Cisco** leads most **planning, design, logical build, and migration** activities under change control; **MGM** provides **readiness, access, applications ownership, and production cutover participation**.

---

## 1. Why this can feel large — and how we make it controlled

- **Migrations of this class are “process-heavy,” not “mystery-heavy.”** There is a repeated pattern: *understand what you have* → *design templates* → *test in a lab* → *pilot* → *scale* → *stabilize* → *hand to operations*.  
- **A short “freeze” and a bounded “cutover night” are normal** so that what we move to Cisco is **known, tested, and matchable** to the old state (see your preliminary *PRELIMINARY Project Plan*).  
- **Cisco is positioned to run program governance and the bulk of the migration workstream**; MGM’s job is to be **ready on time** for items only you can supply (applications validation, change windows, identity/PKI, credentials via approved process, and operational presence during cutovers).  
- **The detailed week-by-week plan** (including *how many firewalls per week*) is **set with the Cisco PM and MGM**; internal drafts are **directional** until baselined.

This framing is meant to **reduce anxiety**: we are not improvising in production; we are following a **staged** model with **checks** at each door.

---

## 2. Roles (plain language)

| Area | **Who typically leads** | **What it means for MGM** |
|------|-------------------------|----------------------------|
| **Program & migration strategy** | Cisco (with MGM leadership) | Steady steering, clear decisions, one scorecard. |
| **Physical install** (rack, power, patch, site logistics) | Technologent (per SOW) + MGM property/facility access | Consistent “ready site” and escorts; as-built info back to the core team. |
| **Design & build** (FMC, templates, policy migration approach) | Cisco + MGM network/security | MGM brings **current** configs, app/criticality input, and lab paths. |
| **Identity / AD / ISE / RADIUS, certificates** | MGM owns the directory and PKI reality; Cisco assists | **Early** joint sessions; credentials only through **approved** channels, never in email/chat long-term. |
| **Change windows & production cutover** | MGM operations/CAB; Cisco/Technologent execute inside the window | Pre-agreed backout, app owners on-call, comms list. |
| **Day-2 run** | MGM (with **Lifecycle Services** / adoption as contracted) | **Knowledge transfer** and *as-built* are explicit exit criteria per wave, not an afterthought. |

*Aligned with the Cisco “Firewall & Secure Access” proposal: MGM supplies items like **portable** rule data, **counts** of ACLs/NAT, **backup configs**, **lab** for validation, **certs/PKI** engagement, and **hands-on** support during cutovers.*

---

## 3. Phased **timeline** (high level)

Two inputs inform this view: the **Cisco sample global timeline (weeks)** in the proposal deck and the **preliminary** MGM technical sequence (property flow, **freeze**, **migration window**). Real dates are **baselined** in the project plan once the Cisco PM and MGM lock scope and site order.

| Phase | **Intent** | **Typical content** (what people see happening) |
|--------|------------|--------------------------------------------------|
| **1 — Technical discovery & readiness** | Build a shared picture: what Palo does today, what must match on Cisco, and what is out of scope. | VPN/crypto alignment, critical application list, firewall **priority** list for site surveys, diagrams, FMT/assessment of configs, log/SIEM approach, “what passwords/credentials are needed, through which process” clarified **without** sharing secrets in the wrong place. |
| **2 — Solution design & lab** | Turn “what we have” into **templates** and a **tested** path. | FMC/infra compatibility and upgrade path, **lab** import/conversion, golden templates (proposal cites **4 templates for 5 site types**), Nishad/report alignment, manual fixes where the tool is partial, **MOP/CRD**-style hardening. |
| **3 — First property / pilot pattern** | Prove the **pattern** (not just a box) before scaling. | Validate L1/L2, register to FMC, controlled **freeze**, FMT with eyes on *unsupported* / *partial* features, then **cutover** pattern (activate FTD, retire Palo path, validate, app sign-off, failover test). *Your preliminary text uses a **5–10 day** change-freeze and named steps like **no shut** / **shut** / **clear arp** — the exact MOP is formalized in engineering docs.* |
| **4 — Scale** | Repeat the **proven** pattern on the remaining properties. | Wave schedule (how many per week) agreed with **MGM operations capacity**; per-site “high touch” and hypercare, then handoff to **steady** operations. |
| **5 — Stabilize & handover** | Confidence for MGM teams. | Training, as-built, SIEM/ops runbooks, lifecycle/adoption touchpoints. |

**Proposal slide reminder:** The deck shows a *sample* **~32+ week** global program arc from requirements through test/plan, rack & stack, pilot, scale, support, and KT. Your team should treat that as **illustrative** until a **named** timeline is published by the Cisco PM.

**Pilot / scale (proposal):** *Pilot at **4** sites, then **scale to remaining ~24** sites* — final counts follow **actual** inventory and risk decisions.

---

## 4. **Prerequisites** (what must be true before “go” to each major gate)

These are grouped for **MGM** vs **partners** so accountabilities are clear.

### MGM — organizational / program

- **Critical application list and test plan** agreed (owners, what “good” looks like post-cut).  
- **Change windows and migration rate** (e.g. migrations per week) that **operations and apps** can support — **review the draft schedule and explicitly approve or adjust** (per action list).  
- **CAB/change** process: backout, comms, and on-call for **pilot and each wave**.  
- **One place for the truth** (e.g. OneNote/SharePoint links maintained — action item) so nobody hunts through email.  

### MGM — technical readiness

- **Accurate, exportable** Palo **configs** and **portable** rule data for FMT/assessment; process to **refresh** exports before the freeze when needed.  
- **VPN** inventory and alignment: identify **Phase 1/2** encryption compatibility — especially **tunnels** that are partial/unsupported; **19 active** tunnels were called for focused review.  
- **FMC and FTD** infrastructure: version/compatibility and **upgrade** path (e.g. **FMC v10** and existing **FMC 4600** **IPs** for planning); early **AD user agent / RADIUS** integration on the management plane **where possible** before all hardware is in every building.  
- **Site survey** outputs: e.g. **rack elevation** and exact **placement** for **hostname** planning; **Mandalay Bay** called out for review of completeness.  
- **Logging / cyber**: finalize **ingestion** method (e.g. teams named in action list); vulnerability integration docs routed to the **cyber defense** org.  
- **Credentials & admin**: chassis/FMC/FTD access for **authorized** project staff via MGM policy (partners name points of contact; **not** by pasting long-lived secrets into chat).  

### Cisco & Technologent (summary)

- **Cisco:** FMT/assessment outcomes, design/templates, MOP, migration window scripting alignment (including **pre/post** checks: session, latency, etc. — *who runs what* documented so MGM is not guessing). **SCC** demo/ordering path as needed.  
- **Technologent (per SOW):** site survey, rack/stack, labeling, **as-builts** back to the program; support **smart-hands** during **cut** windows as contracted.  
- **Joint:** TAP/visibility where required (e.g. NetScout) — *scheduled* with the right people on the first invite.

---

## 5. **The migration “heartbeat” (per site / wave)** — in human terms

This merges the **preliminary** written sequence with the proposal’s methodology.

1. **Site is physically ready** — power, path, and interfaces match design. **Technologent** and MGM facilities close **site survey** gaps.  
2. **Register to FMC** and bring **management** up healthily.  
3. **Pull / convert** the migration config** in a **controlled** way; **no casual changes** on the Palo for **5–10 days** (the **freeze**) so what we test is what we **cut over**.  
4. **During the freeze** — FMT/translation, hand-fixes, and **parity** reviews with clear **risk** notes.  
5. **Migration window** (approved change) — app owners **pre-validate** readiness; **turn up** FTD path, **turn down** Palo path, **ARPs** and routing steps per MOP, **show commands** and app checks, **pair** with failover tests where required.  
6. **After** — short period of **high-touch** response, **KT** and runbooks, then return to **normal** ops with lifecycle content as purchased.

*If a term like “**ACME** property first” is still a placeholder name in internal drafts, replace with the **true** first site in the final plan once MGM approves.*

---

## 6. From **action items** to **buckets** (reassurance list)

The internal *Palo to Cisco … Action Items* log is long; for stakeholders, the same work rolls up to a handful of **themes**:

| Theme | **Why it matters** | **Outcome we want** |
|--------|--------------------|----------------------|
| **SCC / lab / ordering** (e.g. MGM SCC, product on SCC) | We need **entitlements** and **right versions** in the test path. | **Demo/ordering/activation** is understood and not a surprise the week of cut. |
| **Config truth & FMT** | Gaps = risk. | A **signed** “what moved / what didn’t / why” per site class. |
| **VPN & crypto** | Partial support = manual or redesign. | **Tunnels** ranked; owners for each **exception**. |
| **FMC + identity early** | Late identity work delays tests. | **RADIUS/AD/ISE**-related integration **exercised** in lab before the last minute. |
| **Surveys & physical** | Bad rack data = re-work and hostname/IP churn. | **Nexar/hostname** inputs and **elevation** complete **before** last-minute scrambles. |
| **Borgata / COP** edge cases | Special verification that gear is really **out of path** before **upgrade**. | **Cleared** in writing for **touch** *that* stack. |
| **Logging & security tooling** | SOC and VM teams need the **same** assurances. | **One** method for log forward; **VM** docs with Mo Baker *distributed*. |
| **Governance artifacts** | Audits and ITIL hygiene. | **MOP/CRD** and **Opex**-ready *as-builts*. |

---

## 7. **Investment & “sample” numbers** (so Finance isn’t a rumor mill)

- The **Firewall** proposal is a **budgetary, turnkey** picture with **6× FPR-3130**, **34× FPR-4215**, and **optional 4× FPR-4245 (DC)**, with **BTA**-style subs and co-invested **PS**; **Cisco Security Cloud Control** is called **optional** vs on-prem **FMC**. **Exact $** belong in the **signed** order and *True Forward* process — **use the commercial package**, not this page, for approvals.  
- A **32-ish week** *sample* **global** Gantt is only that — **yours** may be **shorter or longer** with **pilot gating** and **supply chain**.  
- The deck also states **2026** HW **support** positioning on certain bundles — let **Cisco account team** keep **MGM** aligned with **BTA/True Forward** *mechanics*; this migration plan is about **operational** clarity.

---

## 8. **Risks we talk about in the open** (and mitigate)

- **Policy parity** — *some* features don’t 1:1. Mitigation: **lab**, **pilot**, **explicit** exceptions list, **MOP** sign-off.  
- **App validation** — network can be “green” while the **app** is not. Mitigation: **mandatory** app owner checks in the **window** and a **backout** trigger.  
- **Credential & PKI lead time** — last-minute = delay. Mitigation: **one** process, **one** store, and **names** of approvers.  
- **Overloading weeks** with **too many** firewalls. Mitigation: **hard** cap per wave until **KPIs** (open incidents, false positives, app noise) are **green**.

---

## 9. **Next decisions for MGM to lock (executive level)**

1. **Pilot sites** and **go / no-go** per wave — **one** list, **versioned** (priority may shift after FMT, per proposal *and* your action log).  
2. **App test plan** and **roll-back** *phone tree* — **not** an IT-only item.  
3. **How many** migrations per **week** the org can **absorb** (apps + ops + **Technologent** + Cisco).  
4. **FMC/Cloud** management **final** — pick one **authoritative** control plane for the **build**.  
5. **Communication plan** to properties and **security** — *what* changes for **them**, and *when* it’s “noise, not an incident.”

---

## 10. **Document control**

| Source (internal) | **Use in this summary** |
|--------------------|-------------------------|
| *MGM FW & SA Proposal* PPTX (1.21.26) | Scope, **RACI**-style split, **hardware** classes, **sample** timeline, pilot/scale, commercial framing. |
| *PRELIMINARY Project Plan* DOCX | **Freeze** / **FMT** / **cutover** choreography and site-first **pattern**. |
| *Palo to Cisco Action Items* PDF (04/23/26) | Concrete tasks rolled into **themes** and **prerequisites**. |

**Owner:** Program management (Cisco) with **MGM** IT leadership — **this** document is a **stakeholder** view; replace with **formal** deliverable IDs when PMO **links** the official **MOP/CRD/test plan** set.

---

*Cisco confidential third-party information may appear in source files; this summary avoids copying confidential pricing and internal names except where they are program-management labels. Operational secrets must never be stored in this repository.*
