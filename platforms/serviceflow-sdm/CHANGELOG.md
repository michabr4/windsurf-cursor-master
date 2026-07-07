# Changelog

All notable changes to **ServiceFlow SDM (Helix)** are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added (Phase 2.1 — May 2026)

- JWT secret validation at startup (fail if default outside `development`)
- Rate limiting on auth endpoints (10/15min) and write endpoints (100/15min), configurable via `RATE_LIMIT_*`
- Zod validation on Salesforce case writes and Webex war-room integration
- Production-ready Docker multi-stage builds (Node runtime + nginx for React SPA)
- Mobile Expo config uses default icon/splash until brand assets are added

### Changed

- Docker Compose loads `.env` (gitignored) instead of `.env.example`
- Frontend container serves built static files on port 80 (mapped to host 3001)

### Documented

- Health probe path: `GET /api/v1/health/`
- Run `npm run migrate` from `backend/` before relying on `docker compose up`
- Optional dev placeholder PNGs under `mobile/assets/` for teams adding brand assets early

## [0.1.0] - 2026-05

### Added

- Initial platform with Express backend, React frontend, Expo mobile
- JWT authentication with OIDC SSO support
- PostgreSQL database with migrations and seeds
- Integrations: Salesforce, Cisco DNA Center, TAC, Smart Licensing, Webex war rooms
- HTML mockup hub with 19 views and optional live API mode
- Power BI analytics embedding
- Docker Compose development environment (Postgres, Redis, API, SPA)

### Security

- Secrets via environment only; `.env.example` uses placeholders
- Production must set unique `JWT_SECRET` and `JWT_REFRESH_SECRET` (≥32 characters)

[Unreleased]: https://github.com/michabr4/serviceflow-sdm/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/michabr4/serviceflow-sdm/releases/tag/v0.1.0
