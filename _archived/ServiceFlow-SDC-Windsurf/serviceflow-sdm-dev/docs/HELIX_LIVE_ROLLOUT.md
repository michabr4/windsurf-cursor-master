# Helix live data — build order (low‑prompt handoff)

Follow this sequence so each layer reuses the last; extend the same pattern to new hub tabs.

## 1. Data & API (backend)

1. **Schema** — add tables/columns in `infra/migrations/` (never only in app code).
2. **Route** — `backend/src/routes/<domain>.ts`: `requireAuth` (+ `requireRoles` for mutations), Zod for bodies, `pool.query` with parameters.
3. **Register** — `app.use("/api/v1/<path>", router)` in `src/app.ts`.
4. **Read model** — prefer one **summary** endpoint per hub area when the UI needs many counts (see `GET /api/v1/overview/summary`).

## 2. Helix mockup (static hub)

1. **Live strip** — `mockup-hub.js`: extend `refreshMockupLiveData()` with `mockupFetchJson` to new paths; keep JWT in `localStorage` key used by Operations.
2. **Apply functions** — small `applyLive…` helpers that only touch DOM ids; avoid duplicating business rules in the client when the API can return ready‑to‑show strings.
3. **Registry‑driven UI** — integration cards use `GET /api/v1/admin/sources` (`sourceName`, `enabled`, `schedule`, `updatedAt`, `notes`); wave label is parsed from `notes` (`Wave N`).

## 3. Verify

- `npm run migrate` → `npm run dev` from `backend/`.
- Sign in at `http://localhost:3000/` → open `http://localhost:3000/mockup/` → **Live data** on → **Refresh**.

## 4. Next domains (suggested)

| Hub area        | Likely API additions                                      |
|----------------|------------------------------------------------------------|
| Sentiment / VoC | New integration + summary metrics (no table yet)      |
| Incidents list | Already `/incidents`; add filters/aggregates if needed  |
| DDS (docs)     | New router + tables when product locks contracts      |

Keep mock copy in HTML as fallback; live mode overlays real values where ids exist.
