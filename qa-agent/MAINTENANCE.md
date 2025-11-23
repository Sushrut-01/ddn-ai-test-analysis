# QA Agent Maintenance

Runbook:
- To update tests when the Dashboard UI changes:
  1. Update selectors in `tests/ui/helpers/dashboard-helpers.ts`.
  2. Run `npx playwright test` locally and re-record failing flows if needed.
  3. Update test expectations and add a short note to the PR describing the UI change.

PR Checklist:
- Tests run locally and pass.
- New or updated selectors are documented.
- No credentials are added to the repo.

Troubleshooting:
- If Playwright fails in CI with missing libs, use the Playwright Docker image or run `npx playwright install --with-deps`.
