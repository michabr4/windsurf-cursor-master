# Live inbox with minimal IT

You do **not** need your own Azure app registration for the recommended path. You sign in with **Microsoft’s Graph PowerShell** app (already registered by Microsoft). IT may still need to allow that app in your tenant—many Cisco tenants already do for engineers.

## How this works (no custom Client ID from you)

| Piece | What happens |
|-------|----------------|
| **Auth** | `Connect-MgGraph` opens browser/device login as `michabr4@cisco.com` |
| **App identity** | Microsoft Graph PowerShell’s app (not yours) |
| **Tenant** | Discovered at login—you don’t paste Tenant ID |
| **Mail read** | `Mail.Read` delegated to **your** mailbox only |
| **Our workbench** | PowerShell exports JSON → Python/Cursor runs orchestration **locally** |

“Local” = processing on your Mac. **Microsoft still authenticates you** once per session.

## Prerequisites (on your Mac)

1. **PowerShell 7+** (`pwsh`): https://github.com/PowerShell/PowerShell  
2. **Graph module** (one-time):

   ```powershell
   Install-Module Microsoft.Graph -Scope CurrentUser
   ```

3. **`.env`** (copy from `.env.example`):

   ```env
   MS_MAILBOX_UPN=michabr4@cisco.com
   MS_AUTH_MODE=graph_powershell
   ```

No `MS_CLIENT_ID` or `MS_TENANT_ID` required for this mode.

## First-time sign-in

```bash
./scripts/email_fetch.sh
```

Or in PowerShell:

```powershell
Connect-MgGraph -Scopes Mail.Read
```

Complete login in the browser. Tokens are cached by Microsoft’s auth layer (not in git).

## Fetch mail for orchestration

```bash
./scripts/email_fetch.sh --since-hours 48 --max-messages 40
```

Writes: `data/runs/email/latest/messages.json`

Then in Cursor:

> Follow `agents/orchestrator-email.md` and run `orchestration/email-inbox-review` using `data/runs/email/latest/messages.json`. Draft only.

## Morning digest (after fetch works)

```bash
./scripts/email_fetch.sh --since-hours 24 --max-messages 30
# Then run orchestration email-morning-digest on that JSON
```

Schedule with `launchd` later (see `docs/email/SCHEDULE.md` when added).

## If Graph PowerShell is blocked

Ask IT: *“Is Microsoft Graph PowerShell (`Connect-MgGraph`, Mail.Read) allowed for my user?”*

**Plan B — device code (still minimal, but needs an app ID):**

- You create a **public client** app in Azure Portal (no secret), or IT gives you a Client ID  
- Set `MS_AUTH_MODE=device_code` and `MS_CLIENT_ID=...` in `.env`  
- Run: `python3 python/connectors/microsoft_mail/fetch_device_code.py`

**Plan C — no API:** sample mode or paste threads (see `OVERVIEW.md`).

## Security reminders

- Tokens stay on your machine (Graph module cache / local run dir).  
- Do not commit `data/runs/email/` or `.env`.  
- Fetch script does not send mail or move messages.

## What still needs IT (sometimes)

- Admin consent for Graph PowerShell in locked-down tenants  
- Not the same as registering **your own** app—usually a lighter ask

Use [IT_ADMIN_REQUEST.md](IT_ADMIN_REQUEST.md) only if Graph PowerShell is denied and you need a dedicated app.
