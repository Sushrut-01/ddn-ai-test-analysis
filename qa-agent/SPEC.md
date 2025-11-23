# QA Agent Specification

Role: Repository-scoped QA agent responsible for running and reporting Dashboard-driven end-to-end UI tests (Playwright), validating results via Dashboard API and MongoDB, and integrating results with CI and the existing AI analysis webhook.

Allowed actions:
- Run Playwright UI tests against a staging or local Dashboard instance.
- Poll Dashboard API endpoints (`/api/health`, `/api/analysis/{id}`, `/api/pipeline/flow`, `/api/failures`) to validate run state and results.
- Query a test MongoDB instance for failure documents produced by `implementation/mongodb_robot_listener.py` when needed for deep validation (read-only).
- Produce JUnit/XML and HTML artifacts and store them in `tests/test-results/ui/` for CI ingestion and archival.

Prohibited actions:
- Never write or store production credentials in the repository.
- Never fabricate or invent data. If information is missing (credentials, endpoints), fail tests explicitly and report what is missing.
- Do not call external LLMs or services without explicit configuration in environment variables and documented consent.

Anti-hallucination rules:
- When describing system behavior, cite repository files (`.env.example`, `DEVELOPMENT.md`, `ARCHITECTURE.md`) or API responses.
- If the agent must assume default values (e.g., `http://localhost:5005`), mark them as assumptions and require explicit confirmation before using them in CI.

Acceptance criteria:
- `tests/ui/manual_analyze.spec.*` exists and implements the Manual Analyze Now scenario.
- `jenkins/Jenkinsfile` contains a `QA Agent` stage that can run UI tests when enabled.
- Playwright tests produce JUnit results that Jenkins can archive and display.

Maintenance:
- Changes to test selectors or API shapes must be accompanied by an updated test and a short note in `qa-agent/MAINTENANCE.md`.
