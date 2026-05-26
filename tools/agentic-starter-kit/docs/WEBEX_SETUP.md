# Webex Setup

This template includes Webex examples that use a Personal Access Token, also called a PAT.

## What A PAT Is

A PAT is a token that lets the Webex API act as you. Treat it like a password.

## Where To Get It

1. Open `https://developer.webex.com`.
2. Sign in.
3. Go to your personal token area.
4. Copy the token.
5. Put it in `.env` as `WEBEX_ACCESS_TOKEN`.

## What The Sample Can Do

- list spaces
- list messages in a space
- list recordings visible to your account
- list transcripts visible to your account
- fetch transcript details for a transcript id

## Important Limits

- You can only read spaces that your account belongs to.
- Messages only come from spaces you can access.
- Recordings may be empty if your account does not have meeting recording access.
- Transcripts may be empty if no transcript was generated or your account lacks access.
- A PAT does not automatically grant admin-wide visibility.

## Safer Usage Pattern

- Use Python or Node to call the Webex API.
- If you build a browser UI, have the browser call your backend, not Webex directly with the PAT.