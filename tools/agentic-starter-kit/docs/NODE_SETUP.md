# Node Setup

Use this page if you want to run the Node starter files.

## Recommendation

Install a current Node.js LTS release.

Why:

- it includes both `node` and `npm`
- it is the most common beginner setup
- it matches how the starter scripts in this repo are written

## What To Install First

Install Node.js LTS from the official Node.js website.

After installation, these commands should work:

```powershell
node --version
npm --version
```

## First-Time Setup

From the repository root:

```powershell
cd node
npm install
```

This creates a local `node_modules` folder for the Node starter only. It is already ignored by git in this template.

## Run The Examples

From the `node` folder:

```powershell
npm run webex
npm run circuit
```

## Common Beginner Notes

- Stay inside the `node` folder when you run the npm scripts above.
- If `node` is not recognized, close and reopen the terminal after installing Node.js.
- `npm install` is usually only needed again after dependencies change.

## What Node Does In This Repo

Node.js lets JavaScript run as backend code instead of only in the browser. In this template, the Node folder is the safe place for JavaScript that needs secrets or private API calls.