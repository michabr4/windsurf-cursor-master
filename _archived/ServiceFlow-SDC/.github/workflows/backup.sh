#!/usr/bin/env bash
# =============================================================================
# ServiceFlow SDM — Backup Script
# =============================================================================
# Creates a timestamped PostgreSQL dump and optionally uploads to S3.
#
# Usage:
#   ./deployments/scripts/backup.sh [--upload-s3]
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.prod.yml"
ENV_FILE="${PROJECT_ROOT}/backend/.env.production"
BACKUP_DIR="${PROJECT_ROOT}/deployments/backups"
UPLOAD_S3=false
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

while [[ $# -gt 0 ]]; do
  case $1 in
    --upload-s3) UPLOAD_S3=true ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
  shift
done

# Load env
set -a
# shellcheck source=/dev/null
source "${ENV_FILE}"
set +a

mkdir -p "${BACKUP_DIR}"

BACKUP_FILE="${BACKUP_DIR}/serviceflow_sdm_${TIMESTAMP}.sql.gz"

echo -e "${YELLOW}Creating database backup...${NC}"
docker-compose -f "${COMPOSE_FILE}" exec -T postgres \
  pg_dump -U "${DB_USER}" "${DB_NAME}" | gzip > "${BACKUP_FILE}"

SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
echo -e "${GREEN}Backup created: ${BACKUP_FILE} (${SIZE})${NC}"

# Keep only last 30 backups
find "${BACKUP_DIR}" -name "*.sql.gz" -type f | sort | head -n -30 | xargs -r rm
echo "Retained last 30 backups."

# Optional: upload to S3
if [[ "${UPLOAD_S3}" == "true" ]]; then
  if command -v aws >/dev/null 2>&1 && [[ -n "${S3_BUCKET:-}" ]]; then
    echo "Uploading to s3://${S3_BUCKET}/backups/..."
    aws s3 cp "${BACKUP_FILE}" "s3://${S3_BUCKET}/backups/$(basename "${BACKUP_FILE}")"
    echo -e "${GREEN}Uploaded to S3 successfully.${NC}"
  else
    echo -e "${RED}AWS CLI not found or S3_BUCKET not set — skipping S3 upload.${NC}"
  fi
fi
