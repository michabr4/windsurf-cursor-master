# Outlook API Access Guide (Microsoft Graph)

This guide walks you through getting Microsoft Graph API access for the **Outlook action-items sample** (`python/examples/outlook_action_items_demo.py`).

For the operational AGT-001 chief-of-staff agent, see `delivery-workbench` (`docs/email/OUTLOOK_AGT001_SETUP.md`).

## What You Need

The sample uses **Microsoft Graph API** with **delegated permissions** (device code flow). This means:

- The agent acts as YOU, not as a service account.
- You sign in once via browser, and the agent reads your mailbox on your behalf.
- No client secret is needed — this is the safest path for a sandbox pilot.

## Step-by-Step: Azure App Registration

### Step 1: Open Azure Portal

Go to: [https://portal.azure.com](https://portal.azure.com)

Sign in with your Cisco Microsoft account.

### Step 2: Navigate to App Registrations

1. Search for **"App registrations"** in the top search bar.
2. Click **"App registrations"** under Services.
3. Click **"+ New registration"**.

### Step 3: Register the App

| Field | Value |
| --- | --- |
| Name | `Agent Factory - Outlook Pilot` |
| Supported account types | **Accounts in this organizational directory only** (Single tenant) |
| Redirect URI | Leave blank (device code flow does not need one) |

Click **Register**.

### Step 4: Copy Your IDs

After registration, you'll see the app overview page. Copy these two values:

| Value | Where to find it | What to put in `.env` |
| --- | --- | --- |
| Application (client) ID | Overview page, top section | `MS_CLIENT_ID` |
| Directory (tenant) ID | Overview page, top section | `MS_TENANT_ID` |

### Step 5: Enable Device Code Flow

1. In the left sidebar, click **Authentication**.
2. Scroll down to **Advanced settings**.
3. Set **"Allow public client flows"** to **Yes**.
4. Click **Save**.

### Step 6: Add API Permissions

1. In the left sidebar, click **API permissions**.
2. Click **"+ Add a permission"**.
3. Select **Microsoft Graph**.
4. Select **Delegated permissions**.
5. Search for and add the permissions listed in the table below.
6. Click **Add permissions**.

| Permission | Purpose | Risk Level |
| --- | --- | --- |
| `Mail.Read` | Read your inbox messages | Green — read-only |
| `User.Read` | Confirm your identity | Green — read-only |

For the pilot, these two permissions are sufficient. You do NOT need:

- `Mail.ReadWrite` (not needed until draft mode)
- `Mail.Send` (blocked until day-45 governance)

### Step 7: Grant Admin Consent (If Required)

Some Cisco tenants require admin consent for Graph permissions.

- If you see a **"Grant admin consent"** button and it's available to you, click it.
- If the button is grayed out, you need to **request consent from your IT admin**.
- The request typically goes through your organization's Azure AD admin or security team.

**What to tell your admin**: "I need delegated Mail.Read and User.Read permissions on a single-tenant app registration for an internal pilot that reads my own mailbox to extract action items. No write or send permissions are requested."

### Step 8: Configure Your `.env` File

Open your `.env` file (copy from `.env.example` if it doesn't exist) and set:

```ini
MS_TENANT_ID=your-directory-tenant-id
MS_CLIENT_ID=your-application-client-id
MS_MAILBOX_USER=
MS_OUTLOOK_MAX_MESSAGES=40
```

Leave `MS_MAILBOX_USER` blank to read your own mailbox (recommended for pilot).

### Step 9: Test the Connection

Run the existing demo to confirm access:

```bash
cd python
pip install -r requirements.txt
python examples/outlook_action_items_demo.py
```

This will:

1. Open a device code flow (prints a URL and code in your terminal).
1. You paste the code into a browser and sign in.
1. The agent reads your inbox and outputs prioritized action items.

If this works, your API access is confirmed and the starter samples can use Graph.

## Permission Upgrade Path (Future)

| Phase | Permission Needed | When to Request |
| --- | --- | --- |
| Read-only pilot (now) | `Mail.Read`, `User.Read` | Step 6 above |
| Draft mode (day 15–21) | `Mail.ReadWrite` | After read-only pilot proves stable |
| Team mailbox (day 22+) | `Mail.Read.Shared` | After personal mailbox pilot succeeds |
| Autonomous send (post day-45) | `Mail.Send` | Only after governance approval |

Each upgrade requires a new admin consent grant. Plan for 1–3 business days per approval.

## Troubleshooting

### "AADSTS700016: Application not found"

- Double-check `MS_CLIENT_ID` matches the Application (client) ID on the overview page.

### "AADSTS65001: User or admin has not consented"

- Admin consent is required. Contact your Azure AD admin.

### "ProxyError" or connection timeout

- Corporate proxy is blocking `login.microsoftonline.com` or `graph.microsoft.com`.
- Ask IT to allowlist both domains.
- Check `HTTP_PROXY` / `HTTPS_PROXY` env vars.

### "HTTP 403" from Graph API

- Your account may not have a mailbox (service accounts sometimes don't).
- Confirm your sign-in account has an active Exchange Online mailbox.

### Empty results (no action items)

- Increase `MS_OUTLOOK_MAX_MESSAGES` in `.env` (try 100).
- The scoring threshold filters out low-signal emails. This is expected behavior.

## Security Notes

- **No client secret is stored.** Device code flow uses public client auth.
- **Token is cached in memory only.** It's not written to disk by default.
- **Permissions are read-only.** The agent cannot modify, delete, or send email with `Mail.Read` alone.
- **Single-tenant registration.** Only your organization's accounts can use this app.

## Related Documents

- `delivery-workbench/docs/reference/agent-factory/` — AGT-001 and agent-chain architecture (operational)
- `docs/SECURITY_APPROVAL_CHEAT_SHEET.md` — Green approval for read-only
- `docs/ENV_VARS.md` — Outlook variable reference
