# Flerken — Personal AI Assistant

**Email Triage & Daily Digest** powered by GPT-4o and Microsoft Graph.

Flerken scans your Outlook inbox, triages every email into priority categories, drafts replies for action items, and delivers a beautiful HTML digest straight to your inbox.

---

## What It Does

1. **Fetches** your recent emails via Microsoft Graph API
2. **Triages** each email using GPT-4o into: Urgent, Action Required, FYI, Low Priority
3. **Drafts replies** for emails that need a response
4. **Generates** an executive summary of your inbox
5. **Sends** a formatted HTML digest email to you

---

## Quick Start

### 1. Prerequisites

- **Python 3.11+** installed
- **OpenAI API key** — [Get one here](https://platform.openai.com/api-keys)
- **Azure App Registration** — for Outlook access (see below)

### 2. Install Dependencies

```bash
cd "Flerken - Personal AI Assistant"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 4. Run

```bash
python run.py
```

On first run, Flerken will show a device-code login prompt:
```
┌─────────────────────────────────────────────┐
│  🔐  Flerken needs Outlook access            │
│                                               │
│  Open: https://microsoft.com/devicelogin      │
│  Code: ABCD1234                               │
│                                               │
│  Waiting for you to sign in...                │
└─────────────────────────────────────────────┘
```

Open the URL in your browser, enter the code, sign in with your Microsoft account, and Flerken takes it from there.

---

## Azure App Registration (One-Time Setup)

This is needed so Flerken can read your email. Takes about 5 minutes.

### Step-by-Step

1. Go to [Azure Portal → App registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Click **New registration**
   - Name: `Flerken Personal Assistant`
   - Supported account types: **Single tenant** (your org only)
   - Redirect URI: leave blank (we use device-code flow)
3. Click **Register**
4. Copy the **Application (client) ID** → paste into `.env` as `AZURE_CLIENT_ID`
5. Copy the **Directory (tenant) ID** → paste into `.env` as `AZURE_TENANT_ID`
6. Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions**
   - Add: `Mail.Read`, `Mail.Send`, `User.Read`
7. Click **Grant admin consent** (if you have admin rights) or ask your IT admin
8. Go to **Authentication** → Under **Advanced settings**:
   - Set **Allow public client flows** to **Yes**
   - Click **Save**

That's it! The device-code flow handles the rest securely — no client secret needed.

---

## Project Structure

```
Flerken - Personal AI Assistant/
├── run.py                  # Entry point — run this
├── requirements.txt        # Python dependencies
├── .env.example            # Config template (copy to .env)
├── .gitignore
├── README.md
├── out/                    # Generated digests saved here
│   └── latest_digest.html
└── src/
    ├── __init__.py
    ├── config.py           # Environment & settings loader
    ├── outlook_client.py   # Microsoft Graph API (email fetch/send)
    ├── llm_client.py       # OpenAI GPT-4o (triage & summarization)
    ├── digest_builder.py   # Pipeline orchestrator + HTML template
    └── main.py             # CLI entry point with Rich formatting
```

---

## How Triage Works

| Category | Definition | Examples |
|----------|-----------|---------|
| **Urgent** | Time-sensitive, needs attention within hours | Escalations, outages, exec requests |
| **Action Required** | Needs response within 1-2 days | Project asks, meeting follow-ups |
| **FYI** | Informational, no action needed | Status updates, announcements |
| **Low Priority** | Can be skimmed later | Newsletters, automated notifications |

---

## Security Notes

- **No credentials in code** — all secrets live in `.env` (gitignored)
- **Device-code auth** — no client secret stored; tokens are short-lived
- **Read-only email access** — `Mail.Read` permission only reads, never modifies
- **Draft-first replies** — Flerken suggests replies but never sends without your approval
- **Local processing** — email content is sent to OpenAI's API for summarization; review their [data usage policy](https://openai.com/policies/api-data-usage-policies)

---

## Future Phases

- [ ] **Phase 2:** Web dashboard for reviewing drafts and one-click send
- [ ] **Phase 3:** Calendar integration (meeting prep + briefing)
- [ ] **Phase 4:** Task tracking (Airtable/Asana integration)
- [ ] **Phase 5:** All-in-one morning briefing
- [ ] **Scheduled runs:** Cron/launchd for automatic daily digest

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `AADSTS7000218: request body must contain client_assertion` | Make sure **Allow public client flows** is enabled in Azure portal |
| `403 Forbidden` on email fetch | API permissions not granted — check admin consent |
| `openai.AuthenticationError` | Check your `OPENAI_API_KEY` in `.env` |
| Empty digest | Check `LOOKBACK_HOURS` and `EMAIL_SCAN_COUNT` in `.env` |
