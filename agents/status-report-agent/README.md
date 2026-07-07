# Status Report Agent

**Agent #1 from Helix Agentic Framework V3**

An AI-powered agent that automatically generates weekly status reports by querying Salesforce and ServiceNow, then using Azure OpenAI to create executive narratives.

## Overview

| Attribute | Value |
|-----------|-------|
| **Roles Served** | SDM · PM · PgM |
| **Feasibility** | VERY HIGH |
| **Build Effort** | 2-3 sprints |
| **Before** | 2-3 hrs manual/role/week |
| **After** | <10 min weekly review |

## Features

- **Multi-Source Data Collection**
  - Salesforce: Cases, opportunities, accounts
  - ServiceNow: Incidents, changes, tasks/projects

- **Intelligent Metrics Calculation**
  - Case volume, age, priority distribution
  - Incident MTTR, SLA compliance
  - Change success rates
  - Task completion and overdue tracking

- **LLM-Powered Narratives**
  - Executive summary generation
  - Automatic highlight/concern extraction
  - Role-specific perspective (SDM vs PM vs PgM)

- **Multiple Output Formats**
  - Markdown (default)
  - HTML (styled for email/web)
  - JSON (for integrations)

- **Automated Delivery**
  - GitHub Actions weekly cron
  - Manual trigger with parameters
  - Artifact storage for 30 days

## Quick Start

### 1. Install Dependencies

```bash
cd status-report-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Run the Agent

```bash
# Basic run with defaults
python main.py

# SDM report for last 7 days
python main.py --role SDM --days 7

# PM report filtered to specific account
python main.py --role PM --account "Acme Corp"

# Save in all formats
python main.py --all

# Verbose output
python main.py --verbose
```

## Configuration

### Required Credentials

#### Salesforce
- `SF_INSTANCE_URL` - Your Salesforce instance URL
- `SF_USERNAME` - Salesforce username
- `SF_PASSWORD` - Salesforce password
- `SF_SECURITY_TOKEN` - Security token (from Salesforce settings)

#### ServiceNow
- `SN_INSTANCE_URL` - Your ServiceNow instance URL
- `SN_USERNAME` - ServiceNow username
- `SN_PASSWORD` - ServiceNow password

#### Azure OpenAI
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `AZURE_OPENAI_KEY` - API key
- `AZURE_OPENAI_DEPLOYMENT` - Deployment name (e.g., `gpt-4o`)

### Agent Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `LOOKBACK_DAYS` | 7 | Days to look back for data |
| `AGENT_ROLE` | SDM | Role perspective (SDM, PM, PgM) |
| `OUTPUT_DIR` | ./output | Directory for saved reports |
| `OUTPUT_FORMAT` | markdown | Default format (markdown, html, json) |
| `ACCOUNT_FILTER` | (none) | Filter by Salesforce account |

## CLI Reference

```
usage: main.py [-h] [--role {SDM,PM,PgM}] [--days DAYS] [--account ACCOUNT]
               [--group GROUP] [--output {markdown,md,html,json}]
               [--output-dir OUTPUT_DIR] [--all] [--no-save] [--verbose] [--quiet]

Options:
  --role, -r      Role perspective (SDM, PM, PgM)
  --days, -d      Number of days to look back
  --account, -a   Filter by Salesforce account name
  --group, -g     Filter by ServiceNow assignment group
  --output, -o    Output format
  --output-dir    Directory to save reports
  --all           Save in all formats
  --no-save       Print to console only
  --verbose, -v   Enable debug logging
  --quiet, -q     Suppress console output
```

## GitHub Actions Setup

### 1. Add Repository Secrets

Go to Settings → Secrets and variables → Actions, and add:

- `SF_INSTANCE_URL`
- `SF_USERNAME`
- `SF_PASSWORD`
- `SF_SECURITY_TOKEN`
- `SN_INSTANCE_URL`
- `SN_USERNAME`
- `SN_PASSWORD`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_DEPLOYMENT`

### 2. Enable Workflow

The workflow runs automatically every Monday at 7:00 AM UTC.

To trigger manually:
1. Go to Actions → Weekly Status Report
2. Click "Run workflow"
3. Select role, lookback days, and optional account filter

## Architecture

```
status-report-agent/
├── main.py              # CLI entry point
├── agent.py             # Main orchestrator
├── config.py            # Settings management
├── models.py            # Pydantic data models
├── salesforce_client.py # Salesforce API integration
├── servicenow_client.py # ServiceNow API integration
├── llm_client.py        # Azure OpenAI integration
├── report_generator.py  # Report formatting
├── requirements.txt     # Dependencies
├── .env.example         # Configuration template
├── .github/
│   └── workflows/
│       └── weekly-report.yml  # GitHub Actions workflow
└── README.md
```

## Data Flow

```
┌─────────────┐     ┌──────────────┐
│ Salesforce  │────▶│              │
│  (Cases)    │     │              │
└─────────────┘     │              │     ┌─────────────┐
                    │    Agent     │────▶│  LLM (GPT)  │
┌─────────────┐     │ Orchestrator │     │  Narrative  │
│ ServiceNow  │────▶│              │     └─────────────┘
│ (Incidents) │     │              │            │
└─────────────┘     └──────────────┘            ▼
                           │              ┌─────────────┐
                           └─────────────▶│   Report    │
                                          │  (MD/HTML)  │
                                          └─────────────┘
```

## Sample Output

```markdown
# Weekly Status Report — SDM
**Period:** Jan 1 - Jan 7, 2025

## Executive Summary

Overall status: **GREEN** ✅

This week showed strong operational performance with SLA compliance 
at 94.2%, exceeding our 90% target. We resolved 23 incidents with 
an average MTTR of 4.2 hours...

### ✅ Key Highlights
- SLA compliance improved from 91% to 94.2%
- Zero P1 incidents this week
- Closed 15 cases, reducing backlog by 12%

### ⚠️ Concerns
- 3 cases aging beyond 14 days require attention
- Change success rate dropped to 87% (target: 95%)

### 📋 Action Items
- [ ] Review aging cases with account team
- [ ] Conduct change failure analysis for CHG0012345
```

## Extending the Agent

### Adding New Data Sources

1. Create a new client in `{source}_client.py`
2. Add models to `models.py`
3. Update `agent.py` to collect and calculate metrics
4. Update `llm_client.py` to include in narratives

### Custom Report Templates

Modify `report_generator.py` to add custom templates or branding.

### Delivery Channels

Add email or Webex delivery by implementing delivery functions and updating the GitHub Actions workflow.

## Troubleshooting

### Salesforce Authentication Failed
- Verify security token is appended to password
- Check IP restrictions in Salesforce setup
- Ensure API access is enabled for the user

### ServiceNow 401/403 Errors
- Verify user has REST API access
- Check instance URL format (include https://)
- Ensure user has read access to required tables

### LLM Rate Limits
- Reduce `LOOKBACK_DAYS` to process less data
- Use GPT-4o-mini for cost-effective processing
- Implement retry logic for transient errors

## License

Internal Cisco tool - not for external distribution.

---

**Part of the Helix Agentic Framework V3**  
*40 Agents · Role-Based AI · Cisco CX*
