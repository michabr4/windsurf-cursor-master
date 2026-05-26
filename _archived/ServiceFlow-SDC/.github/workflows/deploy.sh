#!/usr/bin/env bash
# =============================================================================
# ServiceFlow SDM — Production Deployment Script
# =============================================================================
# Usage:
#   ./deployments/scripts/deploy.sh [--build] [--migrate] [--seed]
#
# Options:
#   --build     Force rebuild of Docker images
#   --migrate   Run database migrations after deploy
#   --seed      Run database seed after migrations (dev/staging only)
#   --help      Show this help message
# =============================================================================

set -euo pipefail

# ── Colour helpers ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No colour

info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── Defaults ───────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.prod.yml"
ENV_FILE="${PROJECT_ROOT}/backend/.env.production"
BUILD=false
MIGRATE=false
SEED=false

# ── Parse arguments ────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case $1 in
    --build)   BUILD=true ;;
    --migrate) MIGRATE=true ;;
    --seed)    SEED=true ;;
    --help)
      echo "Usage: $0 [--build] [--migrate] [--seed]"
      exit 0 ;;
    *) error "Unknown argument: $1" ;;
  esac
  shift
done

# ── Preflight checks ───────────────────────────────────────────────────────────
info "Running preflight checks..."

command -v docker       >/dev/null 2>&1 || error "Docker is not installed or not in PATH"
command -v docker-compose >/dev/null 2>&1 || command -v "docker compose" >/dev/null 2>&1 || error "Docker Compose is not installed"

[[ -f "${ENV_FILE}" ]]     || error "Production env file not found: ${ENV_FILE}"
[[ -f "${COMPOSE_FILE}" ]] || error "Docker Compose file not found: ${COMPOSE_FILE}"

success "Preflight checks passed"

# ── Load env file for variable substitution ────────────────────────────────────
set -a
# shellcheck source=/dev/null
source "${ENV_FILE}"
set +a

# ── Build images ───────────────────────────────────────────────────────────────
if [[ "${BUILD}" == "true" ]]; then
  info "Building Docker images..."
  docker-compose -f "${COMPOSE_FILE}" build --no-cache
  success "Images built successfully"
fi

# ── Pull latest images (for external base images) ─────────────────────────────
info "Pulling latest base images..."
docker-compose -f "${COMPOSE_FILE}" pull --ignore-pull-failures postgres redis || true

# ── Stop old containers gracefully ────────────────────────────────────────────
info "Stopping existing containers (graceful)..."
docker-compose -f "${COMPOSE_FILE}" stop backend frontend || true

# ── Start infrastructure (DB + Redis) ─────────────────────────────────────────
info "Starting PostgreSQL and Redis..."
docker-compose -f "${COMPOSE_FILE}" up -d postgres redis

info "Waiting for database to be healthy..."
timeout=120
elapsed=0
until docker-compose -f "${COMPOSE_FILE}" exec -T postgres pg_isready -U "${DB_USER}" -d "${DB_NAME}" >/dev/null 2>&1; do
  if [[ $elapsed -ge $timeout ]]; then
    error "Database did not become healthy within ${timeout}s"
  fi
  sleep 2
  elapsed=$((elapsed + 2))
done
success "Database is healthy"

# ── Run migrations ─────────────────────────────────────────────────────────────
if [[ "${MIGRATE}" == "true" ]]; then
  info "Running database migrations..."
  docker-compose -f "${COMPOSE_FILE}" run --rm backend \
    node -e "
      const { Pool } = require('pg');
      const fs = require('fs');
      const pool = new Pool({
        host: process.env.DB_HOST,
        port: process.env.DB_PORT,
        database: process.env.DB_NAME,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD
      });
      const sql = fs.readFileSync('/app/scripts/db/01_schema.sql', 'utf8');
      pool.query(sql).then(() => { console.log('Migrations complete'); pool.end(); })
        .catch(e => { console.error(e.message); pool.end(); process.exit(1); });
    "
  success "Migrations completed"
fi

# ── Seed database ──────────────────────────────────────────────────────────────
if [[ "${SEED}" == "true" ]]; then
  warn "Running database seed (only appropriate for dev/staging)..."
  docker-compose -f "${COMPOSE_FILE}" run --rm backend npm run db:seed
  success "Seed completed"
fi

# ── Start all services ─────────────────────────────────────────────────────────
info "Starting all services..."
docker-compose -f "${COMPOSE_FILE}" up -d

# ── Health check ───────────────────────────────────────────────────────────────
info "Waiting for backend health check..."
timeout=120
elapsed=0
until curl -sf http://localhost:3000/api/v1/health >/dev/null 2>&1; do
  if [[ $elapsed -ge $timeout ]]; then
    warn "Backend did not respond within ${timeout}s — checking logs:"
    docker-compose -f "${COMPOSE_FILE}" logs --tail=30 backend
    error "Backend health check failed"
  fi
  sleep 3
  elapsed=$((elapsed + 3))
done
success "Backend is healthy"

# ── Summary ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ServiceFlow SDM deployed successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "  Frontend:  http://localhost"
echo -e "  Backend:   http://localhost:3000"
echo -e "  API:       http://localhost:3000/api/v1"
echo -e "  Health:    http://localhost:3000/api/v1/health"
echo ""

# Show running containers
docker-compose -f "${COMPOSE_FILE}" ps
