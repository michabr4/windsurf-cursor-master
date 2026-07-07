# GitHub App setup

## 1. Create the app

In GitHub: **Settings → Developer settings → GitHub Apps → New GitHub App**

- **Webhook URL:** `https://<your-api-host>/webhooks/github`
- **Webhook secret:** generate and copy to `GITHUB_WEBHOOK_SECRET`
- **Permissions:** start with read-only metadata; add repo contents / PRs as needed
- **Subscribe to events:** `installation`, `push`, `pull_request` (minimum: `installation`)

Download the **private key** (.pem).

## 2. Configure the API

```bash
cp .env.example .env
```

Set:

```env
GITHUB_APP_ID=123456
GITHUB_WEBHOOK_SECRET=your-webhook-secret
GITHUB_APP_PRIVATE_KEY_PATH=/secure/path/app.private-key.pem
```

## 3. Install on a repository

Install the app on a test repo. Confirm:

```bash
curl http://127.0.0.1:8000/api/github/status
curl http://127.0.0.1:8000/api/github/events
```

## 4. Installation token (server-side)

```bash
curl -X POST http://127.0.0.1:8000/api/github/installations/<installation_id>/token
```

Use the returned token only on the server; never expose it to the browser.
