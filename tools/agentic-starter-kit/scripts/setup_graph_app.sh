#!/usr/bin/env bash
# setup_graph_app.sh — Register a Microsoft Graph app and write env vars
#
# USAGE:
#   cd "tools/agentic-starter-kit"
#   bash scripts/setup_graph_app.sh
#
# WHAT IT DOES:
#   1. Logs you in via device-code (opens Microsoft login in browser)
#   2. Creates an Azure AD app registration named "Agentic-Graph-Client"
#   3. Adds all required delegated permissions:
#        Mail.Read, Mail.Send,
#        Calendars.Read, Calendars.ReadWrite,
#        Chat.Read, Chat.ReadWrite,
#        Team.ReadBasic.All, Channel.ReadBasic.All,
#        Files.Read, Files.ReadWrite,
#        Sites.Read.All, User.Read
#   4. Adds the device-code redirect URI
#   5. Writes MS_CLIENT_ID and MS_TENANT_ID to .env
#
# REQUIREMENTS:
#   - Azure CLI (brew install azure-cli)
#   - Permission to create app registrations in your tenant
#     (usually any non-guest user can; IT admin may need to grant consent)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$ROOT_DIR/.env"
APP_NAME="Agentic-Graph-Client"
REDIRECT_URI="https://login.microsoftonline.com/common/oauth2/nativeclient"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Microsoft Graph App Registration Setup"
echo "═══════════════════════════════════════════════════════"
echo ""

# ── Step 1: Login ────────────────────────────────────────────────────────────
echo "Step 1/5 — Signing in to Azure AD (device-code flow)"
echo "  A URL and code will appear below. Open the URL and enter the code."
echo ""
az login --use-device-code --output none
echo "  ✓ Signed in"
echo ""

# ── Step 2: Get tenant ID ────────────────────────────────────────────────────
echo "Step 2/5 — Resolving tenant ID"
TENANT_ID=$(az account show --query tenantId --output tsv)
echo "  ✓ Tenant ID: $TENANT_ID"
echo ""

# ── Step 3: Create app registration ─────────────────────────────────────────
echo "Step 3/5 — Creating app registration: $APP_NAME"

# Check if app already exists
EXISTING_ID=$(az ad app list \
  --display-name "$APP_NAME" \
  --query "[0].appId" \
  --output tsv 2>/dev/null || true)

if [[ -n "$EXISTING_ID" && "$EXISTING_ID" != "None" ]]; then
  echo "  ℹ  App already exists — reusing (appId: $EXISTING_ID)"
  CLIENT_ID="$EXISTING_ID"
else
  CLIENT_ID=$(az ad app create \
    --display-name "$APP_NAME" \
    --sign-in-audience "AzureADandPersonalMicrosoftAccount" \
    --query "appId" \
    --output tsv)
  echo "  ✓ Created app (appId: $CLIENT_ID)"
fi
echo ""

# ── Step 4: Add delegated API permissions ────────────────────────────────────
echo "Step 4/5 — Adding delegated Graph permissions"

# Microsoft Graph resource ID (constant across all tenants)
GRAPH_RESOURCE="00000003-0000-0000-c000-000000000000"

# Map of scope name → permission ID (delegated, from Graph docs)
declare -A SCOPE_IDS=(
  ["Mail.Read"]="570282fd-fa5c-430d-a7fd-fc8dc98a9dca"
  ["Mail.Send"]="e383f46e-2787-4529-855e-0e479a3ffac0"
  ["Calendars.Read"]="465a38f9-76ea-45b9-9f34-9e8b0d4b0b42"
  ["Calendars.ReadWrite"]="1ec239c2-d7c9-4623-a91a-a9775856bb36"
  ["Chat.Read"]="f501c180-9344-439a-bca0-6cbf209fd270"
  ["Chat.ReadWrite"]="9ff7295e-131b-4d94-90e1-69fde507ac11"
  ["Team.ReadBasic.All"]="485be79e-c497-4b35-9400-0e3fa7f2a5d4"
  ["Channel.ReadBasic.All"]="9d8982ae-4365-4f57-822f-798de547ed58"
  ["Files.Read"]="10465720-29dd-4523-a11a-6a75c743c9d9"
  ["Files.ReadWrite"]="5c28f0bf-8a70-41f1-8ab2-9032436ddb65"
  ["Sites.Read.All"]="205e70e5-aba6-4c52-a976-6d2d46c48043"
  ["User.Read"]="e1fe6dd8-ba31-4d61-89e7-88639da4683d"
)

REQUIRED_SCOPES=()
for SCOPE in "${!SCOPE_IDS[@]}"; do
  PID="${SCOPE_IDS[$SCOPE]}"
  REQUIRED_SCOPES+=("${GRAPH_RESOURCE}/${PID}=Scope")
done

az ad app update \
  --id "$CLIENT_ID" \
  --required-resource-accesses "[
    {
      \"resourceAppId\": \"$GRAPH_RESOURCE\",
      \"resourceAccess\": [
        {\"id\": \"570282fd-fa5c-430d-a7fd-fc8dc98a9dca\", \"type\": \"Scope\"},
        {\"id\": \"e383f46e-2787-4529-855e-0e479a3ffac0\", \"type\": \"Scope\"},
        {\"id\": \"465a38f9-76ea-45b9-9f34-9e8b0d4b0b42\", \"type\": \"Scope\"},
        {\"id\": \"1ec239c2-d7c9-4623-a91a-a9775856bb36\", \"type\": \"Scope\"},
        {\"id\": \"f501c180-9344-439a-bca0-6cbf209fd270\", \"type\": \"Scope\"},
        {\"id\": \"9ff7295e-131b-4d94-90e1-69fde507ac11\", \"type\": \"Scope\"},
        {\"id\": \"485be79e-c497-4b35-9400-0e3fa7f2a5d4\", \"type\": \"Scope\"},
        {\"id\": \"9d8982ae-4365-4f57-822f-798de547ed58\", \"type\": \"Scope\"},
        {\"id\": \"10465720-29dd-4523-a11a-6a75c743c9d9\", \"type\": \"Scope\"},
        {\"id\": \"5c28f0bf-8a70-41f1-8ab2-9032436ddb65\", \"type\": \"Scope\"},
        {\"id\": \"205e70e5-aba6-4c52-a976-6d2d46c48043\", \"type\": \"Scope\"},
        {\"id\": \"e1fe6dd8-ba31-4d61-89e7-88639da4683d\", \"type\": \"Scope\"}
      ]
    }
  ]"
echo "  ✓ Permissions added"
echo ""

# ── Step 5: Add redirect URI for device-code flow ────────────────────────────
echo "Step 5/5 — Adding redirect URI for device-code flow"
az ad app update \
  --id "$CLIENT_ID" \
  --public-client-redirect-uris "$REDIRECT_URI" 2>/dev/null || \
az rest \
  --method PATCH \
  --uri "https://graph.microsoft.com/v1.0/applications/$(az ad app show --id "$CLIENT_ID" --query id --output tsv)" \
  --body "{\"publicClient\":{\"redirectUris\":[\"$REDIRECT_URI\"]}}" \
  --headers "Content-Type=application/json" > /dev/null
echo "  ✓ Redirect URI set: $REDIRECT_URI"
echo ""

# ── Write .env ───────────────────────────────────────────────────────────────
echo "Writing to .env..."

if [[ -f "$ENV_FILE" ]]; then
  # Update existing entries in-place
  if grep -q "^MS_CLIENT_ID=" "$ENV_FILE"; then
    sed -i '' "s|^MS_CLIENT_ID=.*|MS_CLIENT_ID=$CLIENT_ID|" "$ENV_FILE"
  else
    echo "MS_CLIENT_ID=$CLIENT_ID" >> "$ENV_FILE"
  fi
  if grep -q "^MS_TENANT_ID=" "$ENV_FILE"; then
    sed -i '' "s|^MS_TENANT_ID=.*|MS_TENANT_ID=$TENANT_ID|" "$ENV_FILE"
  else
    echo "MS_TENANT_ID=$TENANT_ID" >> "$ENV_FILE"
  fi
  echo "  ✓ Updated existing $ENV_FILE"
else
  echo "MS_CLIENT_ID=$CLIENT_ID" >> "$ENV_FILE"
  echo "MS_TENANT_ID=$TENANT_ID" >> "$ENV_FILE"
  echo "  ✓ Created $ENV_FILE with MS_CLIENT_ID and MS_TENANT_ID"
fi
echo ""

# ── Print Flerken env update reminder ────────────────────────────────────────
FLERKEN_ENV="/Users/michabr4/New Master Folder - Windsurf and Cursor/agents/flerken/.env"
if [[ -f "$FLERKEN_ENV" ]]; then
  sed -i '' "s|^AZURE_CLIENT_ID=.*|AZURE_CLIENT_ID=$CLIENT_ID|" "$FLERKEN_ENV"
  sed -i '' "s|^AZURE_TENANT_ID=.*|AZURE_TENANT_ID=$TENANT_ID|" "$FLERKEN_ENV"
  echo "  ✓ Also updated Flerken .env (AZURE_CLIENT_ID / AZURE_TENANT_ID)"
  echo ""
fi

echo "═══════════════════════════════════════════════════════"
echo "  Setup complete!"
echo ""
echo "  App name:  $APP_NAME"
echo "  Client ID: $CLIENT_ID"
echo "  Tenant ID: $TENANT_ID"
echo ""
echo "  NEXT: Grant admin consent (optional but recommended)"
echo "  Run: az ad app permission admin-consent --id $CLIENT_ID"
echo "  Or:  https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps"
echo "       → $APP_NAME → API permissions → Grant admin consent"
echo "═══════════════════════════════════════════════════════"
