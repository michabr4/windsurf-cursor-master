---
description: Dependency Audit — run pip-audit or npm audit whenever dependencies are added or changed
alwaysApply: false
---

# Dependency Audit Protocol

## When This Rule Applies

Run an audit whenever a task results in:
- Adding or upgrading a package in `requirements.txt`, `pyproject.toml`, or `setup.py`
- Adding or upgrading a package in `package.json` or `package-lock.json`
- Running `pip install` or `npm install` with any new package name

## Python Audit

```bash
pip install pip-audit --quiet && pip-audit
```

### Results Handling
- **CRITICAL or HIGH** vulnerability found → `status: "blocked"`, list CVEs in `issues`, do not proceed
- **MEDIUM or LOW** → document in `issues` with severity, continue execution
- **Clean** → note "pip-audit: clean" in `summary`

## Node / JavaScript Audit

```bash
npm audit --audit-level=high
```

### Results Handling
- **HIGH or CRITICAL** → `status: "blocked"`, list affected packages and CVEs in `issues`
- **MODERATE or LOW** → document in `issues`, continue
- **Clean** → note "npm audit: clean" in `summary`

## Audit Skip

Only skip if the task JSON contains `"skip_audit": true` (set by Windsurf explicitly).
Always record in RESULT: `"Audit skipped: skip_audit flag set by Windsurf"`.

## Reporting Format

Add to RESULT `issues` array per finding:
```json
{ "issue": "CVE-2024-XXXX in package@version", "severity": "HIGH", "fix": "Upgrade to package@safe-version" }
```
