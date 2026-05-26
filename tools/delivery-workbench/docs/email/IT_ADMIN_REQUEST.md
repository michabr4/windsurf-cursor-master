# IT request: Microsoft Graph app (email assistant)

Copy, adjust, and send to your identity / cloud admin team. Do not include client secrets in email.

---

**Subject:** Request — Azure AD app registration for personal Graph mail assistant (delegated, read-first)

**Body:**

Hi,

I am building a **local, personal productivity tool** that connects to my **primary work mailbox only** via Microsoft Graph. It does not replace Outlook; it helps with triage, summaries, action extraction, and **draft** replies that I review before sending.

**User / mailbox (single user, delegated auth):**  
`michabr4@cisco.com` — primary mailbox only. No shared mailboxes in v1.

**Application type:**  
- Azure AD app registration (single tenant — our organization)  
- **Delegated** permissions (sign-in as me), not application permissions on all mailboxes  

**Redirect URI (local development):**  
`http://127.0.0.1:8765/oauth/callback`

**Phase 1 permissions (request first):**  
- `Mail.Read`  
- `User.Read`  
- Admin consent required for the organization  

**Phase 2 (separate approval if preferred):**  
- `Mail.ReadWrite` — to create **draft messages** in my mailbox only; I send manually from Outlook  

**What the tool does not do:**  
- Does not send mail without my explicit action in Outlook  
- Does not auto-move or auto-delete mail without a separate confirmation step in the tool  
- Does not run as a background service on shared infrastructure (v1 runs on my Mac; optional local scheduled digest)  
- Does not access shared mailboxes or other users’ mail  

**Security:**  
- Client secret (if used) stored only in a local `.env` file, not in source control  
- Tokens stored locally; not embedded in browser code  

Please let me know:  
1. Whether I may register the app myself or if your team will create it  
2. The **Application (client) ID** and whether a client secret is required  
3. **Tenant ID** for our organization  
4. Timeline for **admin consent** on the permissions above  

Thank you.

---

## After approval

Add to your local `.env` (never commit):

```env
MS_TENANT_ID=<from IT>
MS_CLIENT_ID=<from IT>
MS_CLIENT_SECRET=<if confidential client>
MS_MAILBOX_UPN=michabr4@cisco.com
MS_OAUTH_REDIRECT_URI=http://127.0.0.1:8765/oauth/callback
```

Then run OAuth login (connector docs in `python/connectors/microsoft_mail/README.md`).
