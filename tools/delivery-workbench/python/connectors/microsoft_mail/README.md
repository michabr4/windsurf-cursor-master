# Microsoft Mail connector (Graph)

Primary mailbox: `MS_MAILBOX_UPN` in `.env` (e.g. your work address).

## Recommended: minimal IT (`graph_powershell`)

No custom Tenant ID or Client ID in your `.env`.

1. Install PowerShell 7 (`pwsh`) and Graph module:

   ```powershell
   Install-Module Microsoft.Graph -Scope CurrentUser
   ```

2. `.env`:

   ```env
   MS_MAILBOX_UPN=michabr4@cisco.com
   MS_AUTH_MODE=graph_powershell
   ```

3. Fetch:

   ```bash
   chmod +x scripts/email_fetch.sh
   ./scripts/email_fetch.sh
   ```

Sign in when prompted. Output: `data/runs/email/latest/messages.json`

See [docs/email/MINIMAL_IT.md](../../../docs/email/MINIMAL_IT.md).

## Alternate: device code (needs MS_CLIENT_ID)

Public client app registration (no secret). Set:

```env
MS_AUTH_MODE=device_code
MS_CLIENT_ID=<your-public-client-id>
MS_TENANT_ID=organizations
```

```bash
pip install msal
./scripts/email_fetch.sh
```

## Sample mode (no login)

```bash
./scripts/email_fetch.sh --sample
```

## Custom app (full IT path)

See [docs/email/IT_ADMIN_REQUEST.md](../../../docs/email/IT_ADMIN_REQUEST.md) if Graph PowerShell is blocked.

## Orchestration

After fetch, run email workflows in Cursor using `messages.json` and specs in `orchestration/`.
