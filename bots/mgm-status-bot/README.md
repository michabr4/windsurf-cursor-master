# MGM Status Report Bot

Automated daily status reports for MGM Resorts delivery via Webex, powered by GitHub Actions.

## Features

- 📅 **Automated delivery** - Mon-Fri at 8:00 AM EST
- 📊 **Status reports** - Milestones, risks, action items
- 👥 **Subscriber management** - Edit `subscribers.json`
- 🚀 **Manual trigger** - Run anytime via GitHub Actions

## Setup

### 1. Create GitHub Repository

```bash
cd mgm-status-bot
git init
git add .
git commit -m "Initial commit"
gh repo create mgm-status-bot --private --push
```

### 2. Add secrets (fastest: GitHub CLI on your Mac)

From the repo root, after `brew install gh` and `gh auth login -h github.com`:

```bash
./scripts/setup-github-actions.sh
```

That interactively sets `WEBEX_BOT_TOKEN` (required), optionally `WEBEX_ACCESS_TOKEN` and `OPENAI_API_KEY`, and can trigger a workflow run.

**Manual (web UI):** **Settings** → **Secrets and variables** → **Actions** → add:

| Name | Required |
|------|----------|
| `WEBEX_BOT_TOKEN` | Yes — bot sends DMs ([Bot page](https://developer.webex.com/my-apps) → copy token; if you see HTTP 401, regenerate the bot token and update this secret) |
| `WEBEX_ACCESS_TOKEN` | No — short-lived token for **Integration** (recordings / AI step) |
| `WEBEX_REFRESH_TOKEN` | No — long-lived OAuth refresh for that Integration (see below) |
| `WEBEX_CLIENT_ID` / `WEBEX_CLIENT_SECRET` | Only needed locally or if you automate refresh — Integration credentials |
| `OPENAI_API_KEY` | No — AI transcript summaries |

### Create `WEBEX_REFRESH_TOKEN` (Integration OAuth)

This is **not** the bot token. It comes from a Webex **Integration** app that includes the redirect URI `http://localhost:8080/callback`.

```bash
cd mgm-status-bot
pip install -r requirements.txt
export WEBEX_CLIENT_ID="your_integration_client_id"
export WEBEX_CLIENT_SECRET="your_integration_client_secret"
python oauth_setup.py
```

Complete the browser login. Copy the printed **refresh token** into GitHub → **WEBEX_REFRESH_TOKEN**, and the **access token** into **WEBEX_ACCESS_TOKEN** (refresh before expiry, or use `scripts/exchange_refresh_token.py`).

### 3. Enable GitHub Actions

Actions are enabled by default. The workflow runs automatically **Mon–Fri** on a UTC schedule (see **Schedule** below).

## Managing Subscribers

Edit `subscribers.json`:

```json
{
  "emails": [
    "michabr4@cisco.com",
    "colleague@cisco.com"
  ]
}
```

Commit and push changes:

```bash
git add subscribers.json
git commit -m "Add subscriber"
git push
```

## Manual Trigger

1. Go to repo → **Actions** → **MGM Daily Status Report**
2. Click **Run workflow**
3. Click **Run workflow** button

## Schedule

The bot runs at **`23 13 * * 1-5`** — **13:23 UTC** Monday through Friday (about **8:23 AM Eastern Standard Time**; **9:23 AM** during daylight saving). The minute offset avoids the top of the hour, which GitHub documents as a high-load window where scheduled runs can be **delayed or dropped**.

To change the schedule, edit `.github/workflows/daily-report.yml` (`schedule.cron`, UTC). You can also use a [timezone-aware schedule](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule) if you prefer fixed local wall-clock times year-round.

**Note:** Scheduled runs are **at most once per weekday**, not every few hours. There are **no** scheduled runs on Saturday or Sunday.

**If scheduled runs stop:** On **public** repos, GitHub disables scheduled workflows after **60 days** without repository activity — re-enable under **Actions** → workflow → **Enable workflow**.

## Files

| File | Description |
|------|-------------|
| `send_reports.py` | Main script that sends reports |
| `subscribers.json` | List of subscriber emails |
| `.github/workflows/daily-report.yml` | GitHub Actions workflow |

## How Others Subscribe

Share this with your team:

> **Subscribe to MGM Daily Status Reports**
> 
> Email **michabr4@cisco.com** with subject "MGM Subscribe"
> 
> You'll receive status updates Mon-Fri at 8:00 AM EST.
