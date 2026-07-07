Param(
  [ValidateSet("memory", "postgres")]
  [string]$StorageMode = "memory",
  [switch]$WithRedis
)

$ErrorActionPreference = "Stop"

Write-Host "[ServiceFlow] Starting development services..."

$backendDir = "C:\Users\michric2\CursorWindsurf\ServiceFlow SDM\backend"

if ($StorageMode -eq "postgres") {
  Write-Host "[ServiceFlow] Ensuring local Postgres container is running..."
  docker compose -f "$backendDir\docker-compose.postgres.yml" up -d
  Start-Sleep -Seconds 3
}

if (-not $env:JWT_SECRET) { $env:JWT_SECRET = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N") }
if (-not $env:JWT_REFRESH_SECRET) { $env:JWT_REFRESH_SECRET = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N") }
if (-not $env:BOOTSTRAP_ADMIN_EMAIL) { $env:BOOTSTRAP_ADMIN_EMAIL = "admin@serviceflow.local" }
if (-not $env:CORS_ORIGIN) { $env:CORS_ORIGIN = "http://localhost:8080" }
if (-not $env:PORT) { $env:PORT = "3000" }
$env:STORAGE_MODE = $StorageMode

if (-not $env:BOOTSTRAP_ADMIN_PASSWORD) {
  throw "BOOTSTRAP_ADMIN_PASSWORD must be set in your environment before starting."
}

if ($StorageMode -eq "postgres" -and -not $env:DATABASE_URL) {
  throw "DATABASE_URL must be set for STORAGE_MODE=postgres."
}

if ($WithRedis -and -not $env:REDIS_URL) {
  $env:REDIS_URL = "redis://localhost:6379"
}

Set-Location $backendDir

if ($WithRedis) {
  Write-Host "[ServiceFlow] Ensuring local Redis container is running..."
  docker compose -f "$backendDir\docker-compose.redis.yml" up -d
  Start-Sleep -Seconds 2
}

if ($StorageMode -eq "postgres") {
  Write-Host "[ServiceFlow] Running migrations..."
  npm run db:migrate
}

Write-Host "[ServiceFlow] Starting backend API..."
npm run dev
