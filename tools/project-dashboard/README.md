# AI Factory Project Dashboard

Single-page dashboard showing progress, status, blockers, ETAs, and expected outcomes for active workspace projects.

## Run locally

```bash
cd tools/project-dashboard
npm install
npm run dev
```

Open http://localhost:5173/project-dashboard/ (Vite base path) or the URL shown in the terminal.

## Update data

Edit `src/data/projects.json` following the `Project` and `ProjectData` types in `src/types/project.ts`. Keep counts in `summary` aligned with project statuses.

## Add a project

1. Add a new object to the `projects` array in `src/data/projects.json`.
2. Include: `id`, `name`, `category`, `location`, `status`, `phase`, `phase_number`, `progressPct`, `lastUpdated`, `eta`, `blockers`, `completedItems`, `remainingItems`, `expectedOutcome`, `trustTier`.
3. Rebuild or refresh the dev server.

## Build & deploy

```bash
npm run build
```

GitHub Pages deploy workflow: `.github/workflows/deploy-pages.yml` (runs on pushes to `main` under `tools/project-dashboard/`).
