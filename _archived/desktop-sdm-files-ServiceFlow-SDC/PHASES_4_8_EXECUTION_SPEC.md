# Service Delivery Manager - Internal Execution Specification (Phases 4-8)

This document defines the missing implementation details for phases referenced but not provided in the source guide.

## Phase 4 - Backend API Development

### Architecture
- Runtime: Node.js 20 + TypeScript + Express
- Data store: PostgreSQL 15 (`mgm`, `cisco`, `audit` schemas)
- Cache/session/queue: Redis 7
- Realtime: Socket.IO

### API Surface (MVP)
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

### Backend Rules
- Strict input validation for all request bodies.
- Role-based authorization on all mutating endpoints.
- Parameterized SQL only.
- Audit events written on create/update/delete and status transitions.
- No secrets in code; all credentials loaded from environment.

## Phase 5 - Frontend Development

### Pages (MVP)
- Login
- Overview dashboard
- Incident board/list
- Incident detail timeline
- Devices inventory
- Properties list/detail

### Frontend Requirements
- React 18 + TypeScript + Material UI.
- API client with token refresh interceptor.
- Role-aware navigation and route guards.
- Error boundary and user-facing retry states.
- Websocket subscription for incident and sync status updates.

## Phase 6 - Integration Layer

### Integrations
- Cisco DNA Center (inventory + health)
- Cisco TAC API (SR pull/create/update)
- Cisco Smart Licensing (entitlement + consumption)
- WebEx (war room create/post)
- Support APIs (contract, EoX, warranty, bug) after entitlement confirmation

### Execution Model
- BullMQ queues for ingestion jobs.
- Idempotent upserts keyed by external IDs.
- Retry with exponential backoff and capped attempts.
- Job run metadata and failure reason persisted for diagnostics.

## Phase 7 - Testing and Quality Assurance

### Required Test Layers
- Unit tests: validation, auth middleware, integration adapters.
- API integration tests: auth, incidents, devices, properties.
- Contract tests: external adapters with mocked provider responses.
- E2E smoke tests: login -> create incident -> attach TAC metadata -> verify dashboard.

### Release Gates
- Lint and typecheck pass.
- Unit/integration tests pass.
- Secrets scan pass.
- No critical/high known vulnerabilities in dependencies.

## Phase 8 - Deployment

### Non-Prod Deployment Target
- Docker compose for local and shared dev.
- First hosted target: AWS ECS (or EC2) + RDS Postgres + ElastiCache Redis.
- Object storage: S3 for report and attachment artifacts.

### Deployment Requirements
- Zero real secrets in repository.
- `.env.example` complete and validated on startup.
- DB migration runs as deployment step.
- Health checks and readiness checks enabled.
- Structured JSON logging with correlation IDs.

## Cross-Phase Acceptance Criteria
- A developer can run platform locally from fresh clone.
- Core entities (`users`, `properties`, `devices`, `incidents`) are fully operational.
- TAC linkage data is visible on incident detail.
- At least one external sync path (DNA Center or TAC) runs end-to-end in non-prod with test credentials.
