# WebEx_Email_Comm_Intelligence Agent

An AI-powered agent that analyzes your Webex chats, meeting transcripts, and Outlook emails to extract action items, classify conversations by customer vs internal, and prioritize tasks with due dates.

## Features

- **Multi-Source Data Collection**
  - Webex Teams chats (all rooms and direct messages)
  - Webex meeting transcripts
  - Outlook emails via Microsoft Graph API

- **Intelligent Classification**
  - Automatically separates customer conversations from internal discussions
  - Identifies customer names from email domains and conversation context
  - Uses LLM for ambiguous cases

- **Action Item Extraction**
  - AI-powered extraction of tasks and action items
  - Identifies assignees when mentioned
  - Infers due dates from context (e.g., "by EOD", "next week", "ASAP")
  - Falls back to rule-based extraction if LLM unavailable

- **Smart Prioritization**
  - Keyword-based priority detection (urgent, critical, P1, etc.)
  - Context-aware priority escalation for customer-facing items
  - Automatic escalation for overdue or soon-due items

- **Multiple Output Formats**
  - JSON (full structured data)
  - CSV (action items for spreadsheets)
  - Markdown (human-readable reports)
  - Rich console output

## Prerequisites

### 1. Webex Integration

1. Go to [Webex Developer Portal](https://developer.webex.com/docs/getting-started)
2. Get your personal access token (for testing) or create a Webex Integration/Bot
3. Required scopes:
   - `spark:rooms_read`
   - `spark:messages_read`
   - `spark:memberships_read`
   - `spark:people_read`
   - `meeting:recordings_read` (for transcripts)
   - `meeting:transcripts_read` (for transcripts)

### 2. Microsoft Graph API (Outlook)

1. Register an application in [Azure Portal](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps)
2. Configure API permissions:
   - `Mail.Read` (Application permission for daemon app)
   - Or `Mail.Read` (Delegated permission for user-context)
3. Create a client secret
4. Note your Client ID, Tenant ID, and Client Secret

### 3. LLM API (for AI extraction)

Choose one:

- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/)
- **Anthropic**: Get API key from [Anthropic Console](https://console.anthropic.com/)

## Installation

```bash
# Clone or navigate to the project
cd "WebEx_Email_Comm_Intelligence Agent"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

Edit `.env` with your credentials:

```env
# Webex
WEBEX_ACCESS_TOKEN=your_webex_token

# Microsoft Graph
MS_CLIENT_ID=your_azure_client_id
MS_CLIENT_SECRET=your_azure_client_secret
MS_TENANT_ID=your_azure_tenant_id
MS_USER_EMAIL=michabr4@cisco.com

# LLM (choose one)
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
# Or for Anthropic:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=your_anthropic_key

# Agent settings
LOOKBACK_DAYS=7
OUTPUT_FORMAT=json
OUTPUT_DIR=./output
```

## Usage

### Basic Usage

```bash
# Run with all sources, default settings
python main.py

# Run with specific lookback period
python main.py --days 14

# Run with specific sources only
python main.py --sources webex_chat email

# Run without LLM (rule-based extraction)
python main.py --no-llm
```

### Output Options

```bash
# Output to specific format
python main.py --output markdown

# Export to all formats at once
python main.py --output-all

# Custom output directory
python main.py --output-dir ./reports
```

### Verbose Mode

```bash
# Enable debug logging
python main.py --verbose
```

## Output Examples

### Console Output

```text
╭──────────────────────────────────────────────────────────────╮
│         WebEx_Email_Comm_Intelligence Report                  │
│    Generated: 2024-01-15 14:30 | Lookback: 7 days            │
╰──────────────────────────────────────────────────────────────╯

┌─────────────────────────────────────────┐
│                Summary                   │
├───────────────────────────┬─────────────┤
│ Metric                    │       Value │
├───────────────────────────┼─────────────┤
│ Total Conversations       │          45 │
│ Customer Conversations    │          28 │
│ Internal Conversations    │          17 │
│ Total Action Items        │          23 │
│ High Priority             │           5 │
│ Overdue                   │           2 │
└───────────────────────────┴─────────────┘
```

### JSON Output Structure

```json
{
  "generated_at": "2024-01-15T14:30:00Z",
  "summary": {
    "total_conversations": 45,
    "customer_conversations": 28,
    "total_actions": 23
  },
  "action_items": [
    {
      "description": "Send updated proposal to Acme Corp",
      "assignee": "john@cisco.com",
      "due_date": "2024-01-17T17:00:00Z",
      "priority": "high",
      "customer_name": "Acme",
      "source_type": "email"
    }
  ]
}
```

## Priority Logic

Actions are prioritized based on:

1. **Keywords** (configurable in `.env`):
   - HIGH: urgent, asap, critical, escalation, p1, sev1, immediately
   - MEDIUM: important, soon, this week, follow up, action required

2. **Context Escalation**:
   - Customer-facing items get priority boost
   - Items due within 24 hours escalate to HIGH
   - Overdue items escalate to HIGH

3. **LLM Reasoning**:
   - AI considers full conversation context
   - Identifies implicit urgency from tone and content

## Architecture

```text
WebEx_Email_Comm_Intelligence Agent/
├── main.py              # CLI entry point
├── agent.py             # Main orchestrator
├── config.py            # Settings management
├── models.py            # Data models (Pydantic)
├── webex_client.py      # Webex API integration
├── email_client.py      # Microsoft Graph integration
├── action_extractor.py  # LLM + rule-based extraction
├── output_formatter.py  # Report generation
├── requirements.txt     # Dependencies
├── .env.example         # Configuration template
└── README.md            # This file
```

## Programmatic Usage

```python
from config import get_settings
from agent import CommunicationAgent
from output_formatter import OutputFormatter

# Create and run agent
settings = get_settings()
agent = CommunicationAgent(settings)
report = agent.run(lookback_days=7)

# Access results
for action in report.action_items:
    print(f"[{action.priority}] {action.description}")
    if action.due_date:
        print(f"  Due: {action.due_date}")
    if action.customer_name:
        print(f"  Customer: {action.customer_name}")

# Export
formatter = OutputFormatter(settings)
formatter.save_all_formats(report)
```

## Troubleshooting

### Webex Authentication Failed

- Ensure your access token hasn't expired (personal tokens expire in 12 hours)
- For production, use OAuth integration or bot tokens

### Microsoft Graph 401/403 Errors

- Verify application permissions are granted (admin consent required)
- Check that the user email matches the configured account
- Ensure client secret hasn't expired

### No Actions Extracted

- Try increasing `LOOKBACK_DAYS`
- Check that conversations contain actionable content
- Try `--verbose` to see processing details

### LLM Rate Limits

- Use `--no-llm` for rule-based extraction
- Reduce `MAX_MESSAGES_PER_ROOM` in config

## Security Notes

- **Never commit `.env` files** - they contain secrets
- Store credentials in environment variables or secret managers
- Use application permissions sparingly - prefer delegated when possible
- Rotate API keys and tokens regularly

## License

Internal Cisco tool - not for external distribution.
