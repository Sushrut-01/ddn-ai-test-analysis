# QA Agent Environment

Required variables (for local dev use `.env` or provide via environment):
- `DASHBOARD_URL` - base url for Dashboard (default: `http://localhost:5173` for UI; API usually at `http://localhost:5005`).
- `DASHBOARD_API` - base API url (e.g. `http://localhost:5005`).
- `DASHBOARD_TEST_USER` - test user for UI login (if required).
- `DASHBOARD_TEST_PASS` - password for test user.
- `MONGO_URI` - connection string for test MongoDB to verify failure documents (read-only user recommended).

CI recommendations:
- Store `DASHBOARD_TEST_USER`, `DASHBOARD_TEST_PASS`, and `MONGO_URI` in Jenkins credentials and inject them at runtime.
- Use Playwright Docker image in Jenkins agents or run `npx playwright install --with-deps` at the start of the CI job to ensure browser dependencies are available.
