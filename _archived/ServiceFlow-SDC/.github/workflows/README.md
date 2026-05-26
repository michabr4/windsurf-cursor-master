# Service Delivery Manager

Service Delivery Manager is a service delivery management platform focused on MGM GES-West operational workflows.

## Stack
- Backend: Node.js 20, TypeScript, Express, PostgreSQL, Redis
- Frontend: React 18, TypeScript, Vite
- Runtime: Docker Compose

## Quick Start
1. Copy `.env.example` values into local `.env` files as needed.
2. Start infrastructure and apps:
   - `docker compose up --build`
3. Backend health endpoint:
   - `http://localhost:3000/api/v1/health`
4. HTML platform UI (fast path):
   - `http://localhost:3000`
5. Frontend app:
   - `http://localhost:3001`

## Folder Structure
- `backend/` API service and integrations
- `frontend/` web UI
- `infra/` migrations, seed data, deployment and security docs
