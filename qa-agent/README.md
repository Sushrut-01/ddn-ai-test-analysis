# QA Agent

This directory contains the QA agent scaffold responsible for running dashboard-driven Playwright UI tests and integrating results with Jenkins and the AI analysis pipeline.

Quick start

- Local run (recommended for development):

```powershell
cd tests/ui
npm ci
npx playwright test
```

- CI run: Jenkins should run the `test:ci:ui` script which installs dependencies and runs Playwright with JUnit reporting. See `qa-agent/ENVIRONMENT.md` for required environment variables.

Safety and trust
- The QA agent follows the rules in `qa-agent/SPEC.md` (no hallucination, do not store credentials, fail explicitly when missing inputs).
