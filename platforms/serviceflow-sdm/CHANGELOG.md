# Changelog

All notable changes to **ServiceFlow SDM (Helix)** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `CHANGELOG.md` and README sections for API health, optional React app, Docker dev notes, and production secret guidance (HELIX-HARDEN doc pass, May 2026).
- Expanded `.gitignore` for build artifacts and Expo local state.
- Dev placeholder PNGs in `mobile/assets/` (48×48; replace before store release).

### Documented

- Health probe path: `GET /api/v1/health/` (not `/api/health`).
- Docker Compose is **development-oriented** (`npm run dev` in containers); run `npm run migrate` on the host or add an init job before relying on the stack.
- Mobile app requires icon/splash assets under `mobile/assets/` before store or `expo run` builds.

## [0.1.0] - 2026-05-26

### Added

- Canonical platform location: `platforms/serviceflow-sdm/` (PLATFORM-CONSOLIDATE).
- Legacy planning docs index at `docs/legacy/README.md` (ported from archived ServiceFlow SDC).
- Express API with JWT login, OIDC SSO (PKCE), PostgreSQL migrations/seeds, Redis connection.
- Static mockup hub (`backend/public/mockup/`) with theme persistence and optional live API mode.
- Optional React/Vite shell on port **3001** (incidents, devices, properties, Salesforce, Power BI embed).
- Expo mobile client (`mobile/`) with SSO and tab navigation.
- `docker-compose.yml` for Postgres, Redis, backend, and frontend (local dev).

### Security

- Secrets via environment / GitHub Actions only; `.env.example` uses placeholders.
- Production deployments must set `JWT_SECRET` and `JWT_REFRESH_SECRET` to unique 32+ character values (do not use Zod defaults from `backend/src/config.ts`).

[Unreleased]: https://github.com/michabr4/serviceflow-sdm/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/michabr4/serviceflow-sdm/releases/tag/v0.1.0
