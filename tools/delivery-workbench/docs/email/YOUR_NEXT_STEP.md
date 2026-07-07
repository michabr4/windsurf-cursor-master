# Your next step (one-time sign-in)

Setup is done on your machine:

- Portable PowerShell in `.tools/pwsh`
- Microsoft.Graph module installed
- `.env` configured for `michabr4@cisco.com`

## Sign in and fetch live mail

Open **Terminal** (outside Cursor is fine) and run:

```bash
cd ~/Desktop/delivery-workbench
./scripts/run_email_review.sh
```

1. A browser window opens — sign in with **michabr4@cisco.com**.
2. Accept **Mail.Read** if prompted.
3. When fetch finishes, open Cursor and run the orchestration prompt it prints.

If Cisco blocks the app, you’ll see an admin-consent error — forward that to IT or use sample mode:

```bash
./scripts/run_email_review.sh --sample
```

## What was already generated for you

Sample run outputs (no login): `data/runs/email/sample-run-2026-05-26/`
