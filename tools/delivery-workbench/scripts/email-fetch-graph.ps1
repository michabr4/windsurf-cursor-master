# Fetch primary mailbox messages via Microsoft Graph PowerShell (minimal IT).
# Requires: pwsh, Install-Module Microsoft.Graph -Scope CurrentUser
# Env: MS_MAILBOX_UPN (default: signed-in user's /me if empty)

param(
    [int]$SinceHours = 48,
    [int]$MaxMessages = 40,
    [string]$OutFile = ""
)

$ErrorActionPreference = "Stop"

if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Mail)) {
    Write-Error "Microsoft.Graph module not found. Run: Install-Module Microsoft.Graph -Scope CurrentUser"
}

Import-Module Microsoft.Graph.Mail -ErrorAction Stop

$context = Get-MgContext -ErrorAction SilentlyContinue
if (-not $context) {
    Write-Host "Sign in required (browser)..." -ForegroundColor Cyan
    Connect-MgGraph -Scopes "Mail.Read" -NoWelcome
}

$since = (Get-Date).ToUniversalTime().AddHours(-1 * $SinceHours).ToString("yyyy-MM-ddTHH:mm:ssZ")
$filter = "receivedDateTime ge $since"

$mailbox = $env:MS_MAILBOX_UPN
if ([string]::IsNullOrWhiteSpace($mailbox)) {
    $userId = "me"
} else {
    $userId = $mailbox
}

Write-Host "Fetching up to $MaxMessages messages since $since for $userId ..." -ForegroundColor Cyan

$messages = Get-MgUserMessage -UserId $userId -Filter $filter -Top $MaxMessages `
    -Property "id,subject,from,receivedDateTime,bodyPreview,isRead,conversationId" `
    -OrderBy "receivedDateTime desc" `
    -ErrorAction Stop

$normalized = foreach ($m in $messages) {
    $fromAddr = $m.From.EmailAddress.Address
    if (-not $fromAddr) { $fromAddr = "" }
    [PSCustomObject]@{
        id                 = $m.Id
        subject            = $m.Subject
        from               = $fromAddr
        receivedDateTime   = $m.ReceivedDateTime.ToString("o")
        bodyPreview        = $m.BodyPreview
        isRead             = $m.IsRead
        conversationId     = $m.ConversationId
    }
}

if ([string]::IsNullOrWhiteSpace($OutFile)) {
    $OutFile = Join-Path $PSScriptRoot ".." "data" "runs" "email" "latest" "messages.json"
}

$outDir = Split-Path -Parent $OutFile
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$normalized | ConvertTo-Json -Depth 5 | Set-Content -Path $OutFile -Encoding utf8
Write-Host "Wrote $($normalized.Count) messages to $OutFile" -ForegroundColor Green
