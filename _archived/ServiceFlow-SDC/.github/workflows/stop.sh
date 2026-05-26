#!/usr/bin/env bash
# =============================================================================
# ServiceFlow SDM — Stop / Teardown Script
# =============================================================================
# Usage:
#   ./deployments/scripts/stop.sh [--volumes]
#
# Options:
#   --volumes   Also remove persistent volumes (DESTRUCTIVE — data loss)
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.prod.yml"
REMOVE_VOLUMES=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --volumes) REMOVE_VOLUMES=true ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
  shift
done

if [[ "${REMOVE_VOLUMES}" == "true" ]]; then
  echo -e "${RED}WARNING: This will remove all persistent data (PostgreSQL, Redis)!${NC}"
  read -r -p "Are you sure? Type 'yes' to continue: " confirm
  [[ "${confirm}" == "yes" ]] || { echo "Aborted."; exit 0; }
  echo -e "${YELLOW}Stopping services and removing volumes...${NC}"
  docker-compose -f "${COMPOSE_FILE}" down -v --remove-orphans
else
  echo -e "${YELLOW}Stopping services (data preserved)...${NC}"
  docker-compose -f "${COMPOSE_FILE}" down --remove-orphans
fi

echo -e "${GREEN}Services stopped successfully.${NC}"
