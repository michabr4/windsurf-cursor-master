---
description: Comms Retention — cap .comms/completed/ at 20 files; archive older ones to prevent directory bloat
alwaysApply: true
---

# Comms Retention Protocol

## Limits

| Directory            | Retain              | Action when exceeded              |
|----------------------|---------------------|-----------------------------------|
| `.comms/completed/`  | 20 most recent      | Move older to `.comms/archive/`   |
| `.comms/active/`     | Max 3 in-flight     | Alert if exceeded                 |
| `.comms/inbox/`      | No limit            | N/A                               |

## Enforcement

At the end of each session (runs after `session-activity-log` generates its report):

1. Count files in `.comms/completed/`
2. If count > 20:
   - Sort by filename (RESULT-YYYY-MMDD-NNN order is date-sortable)
   - Move all but the 20 most recent to `.comms/archive/`
   - Note in the session brief: "Archived N completed tasks to .comms/archive/"

## Why This Matters

`.comms/completed/` currently has **51 files** and grows every session.
When pipeline status tools scan this directory, response payloads include all file
listings. Capping at 20 files bounds this overhead permanently regardless of
how many sessions run.

At 51 files × ~200 bytes/filename in listings = ~10,000 characters of noise per scan.
Capping at 20 files eliminates ~60% of that overhead immediately.
