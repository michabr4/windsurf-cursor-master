# API Basics

Use this page if words like API, request, response, or endpoint still feel abstract.

## What An API Is

An API is a defined way for one piece of software to ask another piece of software for data or actions.

Plain language: an API is like a service counter with a menu.

- Your app asks for something in a known format.
- The other system replies in a known format.
- Both sides follow the same rules.

## Simple Mental Model

Think of it like ordering at a cafe:

- You ask for one thing from the menu.
- You use the name the cafe expects.
- The cafe gives you back the result.

With software, the menu is the API documentation.

## Common API Terms

- Request: the question your app sends
- Response: the answer the API sends back
- Endpoint: a specific API URL for one kind of action or data
- Token: a secret string that proves who you are
- JSON: a common text format APIs use for data

## How This Repo Uses APIs

This template includes examples for:

- Webex APIs
- CIRCUIT / Cisco-related API flows

Those are examples of external services your code can talk to.

## Safe Pattern

For this repo, the safe beginner pattern is:

```text
Browser UI -> Python or Node backend -> External API
```

Why:

- the browser should not hold private tokens
- backend code can read `.env` safely
- backend code can clean and simplify API data before sending it to the UI

## What Beginners Usually Need To Remember

- You usually need credentials before an API will respond.
- You usually make a request to one endpoint at a time.
- APIs can fail because of permissions, missing data, or wrong credentials.
- A working sample is the fastest way to learn what an API returns.