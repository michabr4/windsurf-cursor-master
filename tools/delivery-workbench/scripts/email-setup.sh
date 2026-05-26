#!/usr/bin/env sh
# One-time setup: portable PowerShell + Microsoft.Graph module
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PWSH="${ROOT}/.tools/pwsh"
VER="7.5.2"
PKG="powershell-${VER}-osx-arm64.tar.gz"
URL="https://github.com/PowerShell/PowerShell/releases/download/v${VER}/${PKG}"

if [ ! -x "$PWSH" ]; then
  echo "Downloading PowerShell ${VER} to .tools/ ..."
  mkdir -p .tools
  curl -fsSL -o "/tmp/${PKG}" "$URL"
  tar -xzf "/tmp/${PKG}" -C .tools
  chmod +x "$PWSH"
  echo "Installed: $PWSH"
fi

echo "Installing Microsoft.Graph module (CurrentUser) ..."
"$PWSH" -NoProfile -Command "
  Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue
  Install-Module Microsoft.Graph -Scope CurrentUser -Force -AllowClobber
  Get-Module Microsoft.Graph -ListAvailable | Select-Object -First 1 Name, Version
"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo ""
echo "Setup complete. Next:"
echo "  ./scripts/email_fetch.sh"
echo "  (Sign in in the browser when prompted.)"
