---
description: API Integration Patterns
globs: **/*.py,**/*.ts,**/*.js
alwaysApply: false
---

# API Integration Patterns

## Authentication Patterns
- Microsoft Graph: Use device-code flow or PKCE for user-delegated auth
- Salesforce: Use OAuth 2.0 JWT bearer or connected app flow
- ServiceNow: Use OAuth 2.0 or basic auth with instance credentials
- Webex: Use bot tokens for automation, integration tokens for user actions
- Cisco APIs (DNA/FMC/ISE/OpenVuln): Use API key or token auth per service docs

## Error Handling
- Always implement retry with exponential backoff for API calls
- Log the HTTP status code, response body (redacted), and request ID
- Distinguish between retriable (429, 500, 502, 503) and non-retriable (400, 401, 403, 404) errors
- Set reasonable timeouts: 30s for standard, 120s for report generation

## Rate Limiting
- Track rate limit headers (X-RateLimit-Remaining, Retry-After)
- Implement client-side throttling before hitting limits
- Use async/await for concurrent API calls with semaphore limiting

## Data Handling
- Never log full API responses in production — redact sensitive fields
- Cache API responses where appropriate (TTL based on data freshness needs)
- Validate API response schemas before processing
