# Service Delivery Manager Backend (MVP)

Production-style MVP API scaffold aligned to the phase spec:

- Node.js + TypeScript + Express
- JWT auth + refresh
- RBAC on mutating endpoints
- Strict schema validation (zod)
- Security middleware (`helmet`, `cors`)
- Audit event capture for sensitive operations
- Storage abstraction with `memory` and `postgres` modes
- Redis/BullMQ queue scaffold for incident and integration jobs
- Test suite with `jest` + `supertest`

## Quick Start

1. Copy env template:
   - `cp .env.example .env`
2. Fill required values in `.env`:
   - `JWT_SECRET`
   - `JWT_REFRESH_SECRET`
   - `BOOTSTRAP_ADMIN_EMAIL`
   - `BOOTSTRAP_ADMIN_PASSWORD`
   - `STORAGE_MODE` (`memory` or `postgres`)
   - `DATABASE_URL` (required when using postgres mode)
   - `REDIS_URL` (optional, enables queueing)
3. Install and run:
   - `npm install`
   - `npm run dev`
   - `npm run dev:worker` (when `REDIS_URL` is configured)

## Quality Commands

- `npm run typecheck`
- `npm run lint`
- `npm test`

## API Surface (MVP)

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/health`
- `GET /api/v1/properties`
- `POST /api/v1/properties`
- `GET /api/v1/devices`
- `POST /api/v1/devices`
- `GET /api/v1/incidents`
- `POST /api/v1/incidents`
- `PATCH /api/v1/incidents/:incidentId`
- `POST /api/v1/incidents/:incidentId/updates`
- `POST /api/v1/incidents/:incidentId/tac-link`
- `GET /api/v1/tac-cases`

## Notes

- Default persistence is in-memory for acceleration and testability.
- Set `STORAGE_MODE=postgres` with a valid `DATABASE_URL` to enable PostgreSQL persistence.
- Set `REDIS_URL` to enable BullMQ queues:
  - `incident-events`
  - `integration-sync`
- Run worker process for queue consumption:
  - `npm run dev:worker`

## Postgres Mode (Recommended)

1. Start local Postgres (Docker):
   - `docker compose -f docker-compose.postgres.yml up -d`
2. Set environment:
   - `STORAGE_MODE=postgres`
   - `DATABASE_URL=postgres://serviceflow_admin:<password>@localhost:5432/serviceflow_sdm`
3. Run migrations:
   - `npm run db:migrate`
4. Start API:
   - `npm run dev`

## Optional: Unified Startup Script

From repo root:

- `pwsh -File "Service Delivery Manager/scripts/dev-up.ps1" -StorageMode memory`
- `pwsh -File "Service Delivery Manager/scripts/dev-up.ps1" -StorageMode postgres`
- `pwsh -File "Service Delivery Manager/scripts/dev-up.ps1" -StorageMode postgres -WithRedis`

`dev-up.ps1` will:
- start Postgres container when requested,
- start Redis container when `-WithRedis` is provided,
- run migrations in postgres mode,
- launch backend API.

### Redis Worker Runbook

1. Start Redis:
   - `docker compose -f docker-compose.redis.yml up -d`
2. Set `REDIS_URL`, then run:
   - API: `npm run dev`
   - Worker: `npm run dev:worker`
