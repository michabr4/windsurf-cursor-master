# Stack Chooser

Use this page if you are not sure whether to start with Python, Node, or a static web UI.

## Choose Python When

- you want scripts or automation
- you want a backend that is easy to read
- you expect to work with APIs, AI libraries, or data processing
- you want a good default for internal tools

Plain language: Python is a common "do work for me" language.

Setup help: [docs/PYTHON_SETUP.md](PYTHON_SETUP.md)

## Choose Node When

- you want JavaScript on the server
- you expect your frontend and backend to share one language
- you want API routes or a lightweight web server
- your team already thinks in JavaScript

Plain language: Node lets JavaScript run as a server instead of only in the browser.

Setup help: [docs/NODE_SETUP.md](NODE_SETUP.md)

## Choose Static Web UI When

- you want a simple browser page
- you want to prototype layout and user experience quickly
- your data can come from mock data or a backend API

Plain language: HTML, CSS, and browser JavaScript create what users see and click.

## Quick Rule Of Thumb

- Need secrets or private API calls: use Python or Node.
- Need only a simple interface: start in `web`.
- Need both a UI and private API access: use `web` plus `node` or `python`.