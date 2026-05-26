# Digitized Delivery Status Report Bot

Automated daily status reports for Digitized Delivery via Webex, powered by GitHub Actions and Webex SpaceLift.

## Features

- 📅 **Automated delivery** - Mon-Fri at 8:00 AM EST
- � **SpaceLift integration** - Pulls all DD Webex space messages + personal space DD references
- 🎥 **Recording analysis** - Transcripts analyzed with AI
- 🧠 **AI-powered insights** - Extracts action items, risks, decisions, and workstream status
- 👥 **Subscriber management** - Edit `subscribers.json`
- 🚀 **Manual trigger** - Run anytime via GitHub Actions

## How It Works

1. **SpaceLift** (`webex_spacelift.py`) discovers all Webex spaces matching "Digitized Delivery", "ISE as Code", "ISAAC", "NAC Parity", etc.
2. Pulls all messages from those spaces (last 7 days by default)
3. Scans your personal/1:1 spaces for DD keyword references
4. **Recordings** (`webex_recordings.py`) pulls meeting recordings from DD participants
5. AI analyzes all data and extracts structured insights
6. **Report** (`send_reports.py`) builds a dynamic status report and sends via Webex bot

## Spaces Monitored

The bot auto-discovers spaces matching these patterns:
- `GES Digitized Delivery | Core Team`
- `MGM Digitized Delivery - ISE as Code Adoption`
- `Digitized Delivery - GES Leader Space`
- Any space containing: *digitized delivery*, *ise as code*, *isaac*, *nac-parity*

## Setup

### 1. GitHub Repository

Already created at `github.com/michabr4/dd-status-bot` (private).

### 2. Add Secrets

Go to repo → **Settings** → **Secrets and variables** → **Actions** and add:

| Secret | Purpose | Required |
|--------|---------|----------|
| `WEBEX_BOT_TOKEN` | Sends messages to subscribers | ✅ Yes |
| `WEBEX_ACCESS_TOKEN` | Reads spaces, messages, recordings | ✅ Yes (for SpaceLift) |
| `OPENAI_API_KEY` | AI analysis of messages/transcripts | Optional |

### 3. Enable GitHub Actions

Actions are enabled by default. The workflow runs automatically Mon-Fri at 8 AM EST.

## Local Usage

### Analyze a SpaceLift export file
```bash
python webex_spacelift.py --export /path/to/spacelift-export.json
```

### Live API: list DD spaces
```bash
export WEBEX_ACCESS_TOKEN="your_token"
python webex_spacelift.py --list-spaces
```

### Live API: full analysis
```bash
export WEBEX_ACCESS_TOKEN="your_token"
export OPENAI_API_KEY="your_key"
python webex_spacelift.py --days 7
```

### List recordings
```bash
python webex_recordings.py --list-only --days 7
```

## Managing Subscribers

```bash
./manage_subscribers.sh add email@cisco.com
./manage_subscribers.sh remove email@cisco.com
./manage_subscribers.sh list
```

## Manual Trigger

1. Go to repo → **Actions** → **Digitized Delivery Daily Status Report**
2. Click **Run workflow**
3. Optionally set `days_back` to change the lookback window

Or via CLI:
```bash
gh workflow run daily-report.yml
```

## Schedule

The bot runs at `0 13 * * 1-5` (8:00 AM EST / 1:00 PM UTC) Monday through Friday.

## Files

| File | Description |
|------|-------------|
| `send_reports.py` | Builds & sends dynamic report (reads `spacelift_analysis.json`) |
| `webex_spacelift.py` | SpaceLift: pulls DD space messages + personal space DD refs |
| `webex_recordings.py` | Pulls & analyzes DD meeting recordings/transcripts |
| `subscribers.json` | List of subscriber emails |
| `manage_subscribers.sh` | Subscriber management CLI |
| `.github/workflows/daily-report.yml` | GitHub Actions workflow |

## How Others Subscribe

> **Subscribe to Digitized Delivery Daily Status Reports**
>
> Email **michabr4@cisco.com** with subject "DD Subscribe"
>
> You'll receive status updates Mon-Fri at 8:00 AM EST.
