# CURSOR TASK: Project Progress Dashboard

> **Issued by:** Windsurf (Architect)  
> **Date:** 2026-05-29  
> **Priority:** HIGH — first executable sprint  
> **Estimated build time:** 2–3 Cursor sessions  
> **Location to build:** `tools/project-dashboard/`

---

## Mission

Build a single-page web dashboard that visually displays the status, progress, blockers, ETA, and expected outcomes for every active project in this workspace. It reads data from `PROJECT_PROGRESS.md` (parsed at build) and a companion `data/projects.json` that you will generate and maintain.

The dashboard must be immediately runnable with no backend — static HTML/JS served locally via Vite, deployable to GitHub Pages.

---

## Tech Stack

| Layer | Choice | Rationale |
| ----- | ------ | --------- |
| Framework | React 18 + Vite | Matches firewall-dashboard pattern in this workspace |
| Styling | Tailwind CSS + Cisco brand palette | Matches AI Factory / firewall-dashboard theme |
| Icons | Lucide React | Lightweight, matches existing pattern |
| Charts | Recharts | Progress bars, donut charts, timeline |
| Data | `data/projects.json` (static, git-tracked) | No backend needed; updated by Cursor |
| Deploy | GitHub Pages via `.github/workflows/deploy-pages.yml` | Already used in workspace |

### Cisco Brand Palette (REQUIRED — match exactly)

```js
// tailwind.config.js
colors: {
  cisco: {
    blue:  '#049fd9',
    dark:  '#171f2d',
    navy:  '#1a2332',
    teal:  '#00bceb',
    green: '#6cc04a',
    sky:   '#64bbe3',
  }
}
```

---

## Directory Structure to Create

```
tools/project-dashboard/
├── .github/
│   └── workflows/
│       └── deploy-pages.yml
├── public/
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── SummaryBar.tsx
│   │   ├── ProjectCard.tsx
│   │   ├── PhaseTimeline.tsx
│   │   ├── BlockersList.tsx
│   │   ├── ProgressRing.tsx
│   │   └── StatusBadge.tsx
│   ├── data/
│   │   └── projects.json      ← you generate this
│   ├── types/
│   │   └── project.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── README.md
```

---

## Data Schema — `src/data/projects.json`

Generate this file based on `PROJECT_PROGRESS.md`. Populate it with the current state of all 14 active projects. Structure:

```json
{
  "lastUpdated": "2026-05-29",
  "summary": {
    "total": 14,
    "onTrack": 8,
    "blocked": 3,
    "stable": 3,
    "plannedAgents": 31
  },
  "projects": [
    {
      "id": "helix",
      "name": "Helix / ServiceFlow SDM",
      "category": "Platform",
      "location": "platforms/serviceflow-sdm/",
      "status": "Stable",
      "phase": "Phase 2.1 — Complete",
      "progressPct": 85,
      "lastUpdated": "2026-05-26",
      "eta": "July 2026 (GitHub Pages publish)",
      "blockers": [],
      "completedItems": [
        "Production-hardened: JWT auth, rate limiting, Zod validation",
        "5 of 7 frontend pages functional",
        "Mobile: Expo SDK 52, API-driven screens",
        "Docker: multi-stage production builds",
        "Security: no hardcoded secrets"
      ],
      "remainingItems": [
        "Dashboard page wiring to live KPIs",
        "Mobile AsyncStorage persistence",
        "Docker build CLI verification",
        "GitHub Pages publish",
        "Live Salesforce/ServiceNow integration"
      ],
      "expectedOutcome": "Full-stack SDM platform serving as data backbone for all AI Factory agents with live integrations and public demo URL.",
      "trustTier": null,
      "phase_number": 2
    },
    {
      "id": "delivery-tracker",
      "name": "Agent 1: Delivery Tracker",
      "category": "AI Agent",
      "location": "agents/delivery-tracker/",
      "status": "In Development",
      "phase": "Phase 1 — Week 5–8",
      "progressPct": 60,
      "lastUpdated": "2026-05-27",
      "eta": "Week 8 (~2026-07-08)",
      "blockers": ["WEBEX_BOT_TOKEN expired — rotate at developer.webex.com"],
      "completedItems": [
        "Agent card written",
        "Full scaffold: main.py, tracker.py, helix_client.py, report_formatter.py",
        "Dockerfile and requirements defined",
        "Tests directory created"
      ],
      "remainingItems": [
        "Helix API client live wiring",
        "Health scoring implementation",
        "Webex card push (needs token rotation)",
        "Cron scheduling via GitHub Actions",
        "Live pilot: 4 consecutive weeks stable"
      ],
      "expectedOutcome": "Daily delivery health report covering 100% of accounts — reduces weekly check from 2–3 hours to 5-minute review.",
      "trustTier": "T1",
      "phase_number": 1
    },
    {
      "id": "risk-sentinel",
      "name": "Agent 2: Risk & Escalation Sentinel",
      "category": "AI Agent",
      "location": "agents/risk-escalation-sentinel/",
      "status": "In Development",
      "phase": "Phase 1 — Week 9 HITL",
      "progressPct": 25,
      "lastUpdated": "2026-05-27",
      "eta": "Week 9 HITL opens (~2026-07-15)",
      "blockers": [
        "Depends on Delivery Tracker live output",
        "WEBEX_BOT_TOKEN expired"
      ],
      "completedItems": [
        "Agent card written"
      ],
      "remainingItems": [
        "Core scaffold (main.py, agent.py, risk rules engine)",
        "Risk rule implementation (P1/P2, SLA breach, health drop, milestone slip, entitlement)",
        "LLM integration for risk summary",
        "Webex interactive card (Escalate/Schedule/Snooze/Dismiss)",
        "45-day HITL logging",
        "Integration with Delivery Tracker JSON"
      ],
      "expectedOutcome": "Predictive risk detection 5–10 days ahead of issues — replaces reactive escalation with proactive intervention.",
      "trustTier": "T2",
      "phase_number": 1
    },
    {
      "id": "business-review-generator",
      "name": "Agent 3: Business Review Generator",
      "category": "AI Agent",
      "location": "agents/business-review-generator/",
      "status": "In Development",
      "phase": "Phase 1 — Week 10 HITL",
      "progressPct": 50,
      "lastUpdated": "2026-05-27",
      "eta": "Week 10 HITL opens (~2026-07-22)",
      "blockers": ["Salesforce MCP delegated read access unconfirmed"],
      "completedItems": [
        "Agent card written",
        "Full scaffold: data_collector.py, llm_writer.py, metrics_calculator.py, reviewer.py",
        "Templates directory created",
        "Tests structure created"
      ],
      "remainingItems": [
        "Salesforce data collector integration (blocked on MCP access)",
        "ServiceNow data integration",
        "Four-pass LLM chain (exec summary, delivery narrative, risk, next quarter)",
        "Output validation — no hallucinated metrics",
        "Webex draft-ready notification",
        "Pilot: ≥ 3 real QBRs delivered"
      ],
      "expectedOutcome": "QBR prep time reduced from 8–12 hours to 30-minute human review of AI-generated draft.",
      "trustTier": "T2",
      "phase_number": 1
    },
    {
      "id": "mgm-status-bot",
      "name": "MGM Status Bot",
      "category": "Bot",
      "location": "bots/mgm-status-bot/",
      "status": "Blocked",
      "phase": "Phase 2.2 — Ops Fix",
      "progressPct": 90,
      "lastUpdated": "2026-05-26",
      "eta": "TBD — unblocks when token rotated",
      "blockers": ["WEBEX_BOT_TOKEN returning 401 — regenerate at developer.webex.com, update GitHub Secret"],
      "completedItems": [
        "Code complete and clean",
        "GitHub Actions cron configured",
        "subscribers.json valid"
      ],
      "remainingItems": [
        "Rotate WEBEX_BOT_TOKEN in GitHub Secrets (ops — no code)",
        "Trigger workflow_dispatch to verify",
        "Optional: add --dry-run mode",
        "Optional: update GHA actions to v5/v6"
      ],
      "expectedOutcome": "Daily automated MGM status delivery restored via GitHub Actions.",
      "trustTier": null,
      "phase_number": 2
    },
    {
      "id": "dd-status-bot",
      "name": "DD Status Bot",
      "category": "Bot",
      "location": "bots/dd-status-bot/",
      "status": "Blocked",
      "phase": "Phase 2.2 — Ops Fix",
      "progressPct": 90,
      "lastUpdated": "2026-05-28",
      "eta": "TBD — unblocks when tokens rotated",
      "blockers": [
        "WEBEX_ACCESS_TOKEN expired",
        "WEBEX_CLIENT_SECRET needs update (new secret from 2026-05-28 rotation)"
      ],
      "completedItems": [
        "Code complete and clean",
        "GitHub Actions configured",
        "P0 token rotation performed 2026-05-28"
      ],
      "remainingItems": [
        "Update WEBEX_CLIENT_SECRET in GitHub Secrets",
        "Refresh WEBEX_ACCESS_TOKEN via oauth_refresh.py",
        "Trigger workflow_dispatch to verify",
        "Optional: update GHA actions from v4→v5"
      ],
      "expectedOutcome": "Daily Digitized Delivery status delivery restored.",
      "trustTier": null,
      "phase_number": 2
    },
    {
      "id": "forge",
      "name": "Forge — Personal AI Assistant",
      "category": "Agent",
      "location": "agents/forge/",
      "status": "Blocked",
      "phase": "Phase 2.3 — Post-email-consolidation upgrade",
      "progressPct": 70,
      "lastUpdated": "2026-05-26",
      "eta": "TBD — blocked by Azure AD registration",
      "blockers": ["Azure AD app not registered in Microsoft Entra — ops required"],
      "completedItems": [
        "Core email digest functionality built",
        "Microsoft Graph device-code auth flow",
        "HTML digest output working",
        "Offline mail fallback mode"
      ],
      "remainingItems": [
        "Register Azure AD app in Entra admin center (ops — no code)",
        "Verify MSAL device code flow end-to-end",
        "Web dashboard for reviewing drafts",
        "Calendar integration"
      ],
      "expectedOutcome": "Fully functional personal AI assistant for morning email briefings and proactive outreach drafting.",
      "trustTier": "T1",
      "phase_number": 2
    },
    {
      "id": "firewall-dashboard",
      "name": "Firewall Dashboard",
      "category": "Tool",
      "location": "tools/firewall-dashboard/",
      "status": "Stable",
      "phase": "Phase 3+ — extensions on demand",
      "progressPct": 75,
      "lastUpdated": "2026-05-27",
      "eta": "No active sprint — Phase 3+",
      "blockers": [],
      "completedItems": [
        "React/Vite + Tailwind + Cisco brand theme",
        "Kanban board with dnd-kit",
        "Gantt view",
        "KPI cards",
        "Asana sync integration"
      ],
      "remainingItems": [
        "Mimir API integration (Wave 18)",
        "Airtable PAT rotation"
      ],
      "expectedOutcome": "Real-time firewall implementation tracking dashboard with Cisco CX branding.",
      "trustTier": null,
      "phase_number": 3
    },
    {
      "id": "delivery-workbench",
      "name": "Delivery Workbench",
      "category": "Tool",
      "location": "tools/delivery-workbench/",
      "status": "Stable",
      "phase": "Phase 3.1 — Evolution to daily driver",
      "progressPct": 40,
      "lastUpdated": "2026-05-26",
      "eta": "June–July 2026",
      "blockers": [],
      "completedItems": [
        "Playbooks and templates",
        "Email orchestration foundation",
        "AGT-001 integration references"
      ],
      "remainingItems": [
        "Agent orchestration layer (YAML workflows)",
        "Morning briefing pipeline (email → triage → calendar → brief)",
        "Webex integration (DMs + space mentions)"
      ],
      "expectedOutcome": "Primary SDM daily-driver: one command triggers morning briefing with email, calendar, Webex, and risk signals.",
      "trustTier": null,
      "phase_number": 3
    }
  ],
  "opsBlockers": [
    {
      "id": "webex-bot-token",
      "title": "Rotate WEBEX_BOT_TOKEN",
      "priority": "CRITICAL",
      "owner": "You",
      "done": false,
      "affectsProjects": ["mgm-status-bot", "dd-status-bot", "delivery-tracker", "risk-sentinel"]
    },
    {
      "id": "webex-access-token",
      "title": "Refresh WEBEX_ACCESS_TOKEN (dd-status-bot)",
      "priority": "CRITICAL",
      "owner": "You",
      "done": false,
      "affectsProjects": ["dd-status-bot"]
    },
    {
      "id": "webex-client-secret",
      "title": "Update WEBEX_CLIENT_SECRET in GitHub Secrets (2026-05-28 rotation)",
      "priority": "HIGH",
      "owner": "You",
      "done": false,
      "affectsProjects": ["dd-status-bot"]
    },
    {
      "id": "azure-ad-registration",
      "title": "Register Azure AD app in Microsoft Entra",
      "priority": "HIGH",
      "owner": "You",
      "done": false,
      "affectsProjects": ["forge"]
    },
    {
      "id": "salesforce-mcp",
      "title": "Confirm Salesforce MCP delegated read access",
      "priority": "HIGH",
      "owner": "You",
      "done": false,
      "affectsProjects": ["business-review-generator"]
    },
    {
      "id": "servicenow-mcp",
      "title": "Confirm ServiceNow MCP access",
      "priority": "HIGH",
      "owner": "You",
      "done": false,
      "affectsProjects": ["risk-sentinel", "business-review-generator"]
    }
  ]
}
```

---

## UI Specification

### Layout (top to bottom)

#### 1. Header
- Animated gradient background (`.cisco-header` class from firewall-dashboard pattern)
- Title: `AI Factory Project Dashboard`
- Subtitle: `Cisco CX · SDM Platform`
- Right: `Last updated: [date]` badge

#### 2. Summary Bar (KPI cards, horizontal row)
- **Total Projects** — white card, large number
- **On Track** — Cisco green badge
- **Blocked** — red badge
- **Stable** — teal badge
- **Phase 0 Ops Items Pending** — orange badge with count

#### 3. Ops Blockers Banner (only if any `done: false`)
- Red/orange top-border card
- Title: `⚠️ Action Required — Ops Blockers`
- List each blocker with priority badge, affected projects, and one-line fix instruction
- Collapses to "N blockers resolved" when all done

#### 4. Project Cards Grid (main content)

Layout: responsive 3-column grid (xl), 2-col (md), 1-col (sm).

Each `ProjectCard` contains:
- **Header row:** Project name (bold) + Status badge + Category tag (small pill: Platform / AI Agent / Bot / Tool)
- **Progress section:** `ProgressRing` component (circular SVG progress ring, Cisco blue fill) + `[N]%` center label + Phase name below
- **ETA row:** calendar icon + ETA string (highlighted orange if "TBD")
- **Blockers:** (if any) red warning box with each blocker listed
- **Completed / Remaining toggle:** Click to expand accordion showing bullet lists
- **Expected Outcome:** italic text at bottom, always visible
- **Trust Tier badge:** (AI agents only) T1 / T2 / T3 colored pill

#### 5. Phase Timeline (below cards)
- Horizontal Gantt-style bar showing all 6 AI Factory phases
- Each phase: colored bar proportional to timeline, shows: phase name, agent count, status icon
- Current date marker (vertical line)
- Tooltip on hover: phase details, exit criteria, ETA

#### 6. Status Legend
- Small footer showing all status colors

---

## Status Badge Colors

| Status | Color |
| ------ | ----- |
| Stable | Cisco green `#6cc04a` |
| In Development | Cisco teal `#00bceb` |
| Blocked | red-500 |
| Planned | slate-400 |
| HITL Active | Cisco blue `#049fd9` |
| Complete | Cisco green dark |

---

## Component Specs

### `ProgressRing.tsx`
SVG circle progress indicator.
- Props: `pct: number`, `size: number`, `strokeWidth: number`, `color: string`
- Stroke: Cisco blue `#049fd9`
- Background track: `#e2e8f0`
- Center label: `{pct}%` in `font-bold text-lg`

### `StatusBadge.tsx`
- Props: `status: string`
- Returns a `<span>` with appropriate background/text color class based on status string

### `PhaseTimeline.tsx`
- Reads `projects.json` phase_number and status
- Renders 6 labeled phase bars using Recharts `BarChart` or custom SVG
- Phase 0: complete (green)
- Phase 1: in progress (teal)
- Phases 2–6: planned (slate)

### `BlockersList.tsx`
- Reads `opsBlockers` array from projects.json
- Renders each blocker as a card with: priority badge, affected project list, fix instruction
- Sort: CRITICAL first

---

## Build Steps for Cursor

### Step 1 — Scaffold

```bash
cd tools
npm create vite@latest project-dashboard -- --template react-ts
cd project-dashboard
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install lucide-react recharts
```

### Step 2 — Configure Tailwind

Create `tailwind.config.js` with this exact content (identical to `tools/firewall-dashboard/tailwind.config.js` — do not deviate):

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        cisco: {
          blue:  '#049fd9',
          dark:  '#171f2d',
          navy:  '#1a2332',
          teal:  '#00bceb',
          green: '#6cc04a',
          sky:   '#64bbe3',
        },
      },
    },
  },
  plugins: [],
}
```

### Step 3 — Generate `src/data/projects.json`

Use the full JSON schema above. Populate with current state from `PROJECT_PROGRESS.md`.

### Step 4 — Create Types (`src/types/project.ts`)

```typescript
export interface Project {
  id: string;
  name: string;
  category: 'Platform' | 'AI Agent' | 'Bot' | 'Agent' | 'Tool';
  location: string;
  status: 'Stable' | 'In Development' | 'Blocked' | 'Planned' | 'HITL Active' | 'Complete';
  phase: string;
  phase_number: number;
  progressPct: number;
  lastUpdated: string;
  eta: string;
  blockers: string[];
  completedItems: string[];
  remainingItems: string[];
  expectedOutcome: string;
  trustTier: 'T1' | 'T2' | 'T3' | null;
}

export interface OpsBlocker {
  id: string;
  title: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  owner: string;
  done: boolean;
  affectsProjects: string[];
}

export interface ProjectData {
  lastUpdated: string;
  summary: {
    total: number;
    onTrack: number;
    blocked: number;
    stable: number;
    plannedAgents: number;
  };
  projects: Project[];
  opsBlockers: OpsBlocker[];
}
```

### Step 5 — Build Components (in order)

1. `StatusBadge.tsx`
2. `ProgressRing.tsx`
3. `ProjectCard.tsx` (uses StatusBadge + ProgressRing)
4. `SummaryBar.tsx`
5. `BlockersList.tsx`
6. `PhaseTimeline.tsx`
7. `Header.tsx`
8. `App.tsx` — assembles all components

### Step 6 — Global CSS (`src/index.css`)

Use this **exact** CSS — sourced directly from `tools/firewall-dashboard/src/index.css` and `content/ai-factory/css/styles.css`. Do not deviate from these values.

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ── Smooth scrolling ── */
html {
  scroll-behavior: smooth;
}

/* ── Cisco Dashboard Theme ── */

@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Exact gradient from firewall-dashboard — 4-stop -45deg with background-size 400% */
.cisco-header {
  background: linear-gradient(-45deg, #171f2d, #1a2332, #04314a, #06506e);
  background-size: 400% 400%;
  animation: gradientShift 14s ease infinite;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.fade-in-up {
  animation: fadeInUp 0.5s ease forwards;
}

/* ── KPI cards — hover lift + Cisco blue glow ── */
.kpi-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(4, 159, 217, 0.12);
}

/* ── Glow effects ── */
.cisco-glow {
  box-shadow: 0 0 20px rgba(4, 159, 217, 0.25);
}
.glow-blue {
  box-shadow: 0 0 20px rgba(4, 159, 217, 0.3);
}
.glow-cisco {
  box-shadow: 0 0 20px rgba(0, 188, 235, 0.3);
}

/* ── Phase timeline progress bar animation ── */
.maturity-bar {
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Scroll-reveal for sections ── */
.section-reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.section-reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ── KPI number count-up animation ── */
@keyframes countUp {
  from { opacity: 0; transform: scale(0.8); }
  to   { opacity: 1; transform: scale(1); }
}
.kpi-number {
  animation: countUp 0.5s ease forwards;
}

/* ── Nav active underline (Cisco blue-to-teal gradient) ── */
.nav-link {
  position: relative;
  transition: color 0.2s ease;
}
.nav-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #049fd9, #00bceb);
  transition: width 0.3s ease;
}
.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}

/* ── Custom scrollbar — matches AI Factory ── */
::-webkit-scrollbar        { width: 8px; height: 8px; }
::-webkit-scrollbar-track  { background: #f1f5f9; }
::-webkit-scrollbar-thumb  { background: #94a3b8; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #64748b; }

/* ── Print styles ── */
@media print {
  .no-print { display: none !important; }
  .cisco-header { background: #171f2d !important; animation: none !important; }
  .section-reveal { opacity: 1 !important; transform: none !important; }
}
```

> **Note:** `@tailwind` directive lint warnings in the IDE are false-positives — Vite/PostCSS processes them correctly.

### Step 7 — `index.html`

Standard Vite HTML with title `AI Factory · Project Dashboard`.

### Step 8 — GitHub Actions Deploy

Create `.github/workflows/deploy-pages.yml`:

```yaml
name: Deploy Project Dashboard
on:
  push:
    branches: [main]
    paths:
      - 'tools/project-dashboard/**'
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
        working-directory: tools/project-dashboard
      - run: npm run build
        working-directory: tools/project-dashboard
      - uses: actions/deploy-pages@v4
        with:
          artifact-path: tools/project-dashboard/dist
```

### Step 9 — `vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/project-dashboard/',
})
```

### Step 10 — README.md

Create a brief README:
- What this dashboard does
- How to run locally: `npm run dev`
- How to update data: edit `src/data/projects.json`
- How to add a project: follow `Project` type schema

---

## Acceptance Criteria

Before marking this task complete, verify all of the following:

- [ ] `npm run dev` launches the dashboard with no console errors
- [ ] `npm run build` produces a clean dist/ (no TypeScript errors)
- [ ] All 9 active projects appear as cards with correct progress %, status, phase, ETA
- [ ] Ops blockers banner shows all 6 current blockers with CRITICAL/HIGH priorities
- [ ] Progress rings render correctly (0–100% fill, Cisco blue)
- [ ] Status badges use correct Cisco colors per status
- [ ] Blocked projects show red warning box with blocker text
- [ ] Phase timeline shows all 6 phases with correct current state
- [ ] Dashboard is responsive: works at 375px, 768px, 1440px width
- [ ] No hardcoded credentials anywhere (CodeGuard compliance)
- [ ] All imports use TypeScript-safe paths (no `any` unless unavoidable)

---

## Report Back

After completing the build, report:

1. Dashboard URL for local preview (`http://localhost:5173`)
2. Screenshot or description of what renders
3. Any acceptance criteria that could not be met and why
4. Recommended next sprint items (e.g., live data sync, GitHub Pages deploy)

---

*Task issued by Windsurf Architect · 2026-05-29 · Reference: `PROJECT_PROGRESS.md`, `ROADMAP.md`, `AI_FACTORY_IMPLEMENTATION_PLAN.md`*
