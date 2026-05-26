# Siri Shortcuts Setup for SDM Agents

Trigger your SDM agents with voice commands like "Hey Siri, MGM status"

## Quick Setup (5 minutes)

### Step 1: Create a GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens?type=beta
2. Click **Generate new token**
3. Name: `SDM Siri Shortcuts`
4. Expiration: 90 days (or longer)
5. Repository access: Select `mgm-status-bot`
6. Permissions: `Actions: Read and write`
7. Click **Generate token**
8. **Copy the token** (starts with `github_pat_...`)

### Step 2: Create iOS Shortcut

1. Open **Shortcuts** app on iPhone
2. Tap **+** to create new shortcut
3. Tap **Add Action**
4. Search for **"Get Contents of URL"**
5. Configure:

**URL:**
```
https://api.github.com/repos/michabr4/mgm-status-bot/actions/workflows/daily-report.yml/dispatches
```

**Method:** POST

**Headers:**
| Key | Value |
|-----|-------|
| Authorization | Bearer YOUR_GITHUB_TOKEN |
| Accept | application/vnd.github.v3+json |
| Content-Type | application/json |

**Request Body:** JSON
```json
{"ref": "master"}
```

6. Name the shortcut: **"MGM Status"**
7. Tap **Done**

### Step 3: Test It

Say: **"Hey Siri, MGM Status"**

The bot will send the status report to all subscribers via Webex!

---

## Additional Shortcuts

### Add Subscriber Shortcut

Create a shortcut that:
1. **Ask for Input** → "What email to add?"
2. **Get Contents of URL** → Triggers a new workflow

For this, we need to add a new GitHub Action workflow (see below).

---

## Advanced: Parameterized Shortcuts

To pass parameters (like email addresses), we'll create a dedicated webhook workflow.
