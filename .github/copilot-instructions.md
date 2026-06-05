################################################################################
# GitHub Copilot Project Instructions                                          #
################################################################################

Purpose:
Provide the assistant (Copilot / AI agents) with clear, stable guidance for this
repository (backend + infra + documentation) now that UI/E2E automation was
split into the separate `ddn-playwright-automation` repo.

Scope (What belongs here):
- Python services, infra configs (docker-compose, Rancher migration assets)
- Jenkins integration assets (pipeline/job XML, build scripts)
- Architecture + operations documentation (all *.md, *.html exports)
- System monitoring & maintenance scripts (PowerShell/Bash/BAT) NOT test code
- Migration guides, recovery plans

Out of Scope (moved or to remain external):
- Playwright test specs, Playwright config, UI test workflows
- Performance/load test harnesses (to be added later in dedicated repos)

Repository Separation:
- `ddn-ai-test-analysis` (this repo): backend/services/docs/tooling
- `ddn-playwright-automation`: all UI/E2E Playwright tests + its own workflows
  Nightly cron (02:00 UTC) and PR/push triggers must live only in that repo.

CI Policy (This Repo):
- No Playwright workflows here. Avoid noisy test failure emails.
- Workflows allowed: build, lint, security scans (to add later), doc validation.
- Keep concurrency groups per workflow type to prevent duplicate runs.

Coding & Documentation Standards:
- Python: prefer explicit function names, avoid one-letter vars, keep modules small.
- Shell/PowerShell/BAT: always echo intent at start, fail fast (`set -e` for bash).
- Scripts must declare: Purpose, Inputs (env vars/params), Side Effects, Exit Codes.
- Architecture docs: consolidate into structured folders (pending task).

Pending High-Level Tasks (tracked separately in todo list):
1. Consolidate architecture docs folder structure.
2. Create `scripts/README.md` and `docs/scripts-index.md` with full script catalog.
3. Classify untracked files (`docs/untracked-files-report.md`).
4. Add Jenkins start/import helpers if still missing.
5. Port normalization & service matrix finalization.

Playwright Testing (Reference Only):
- All active specs + config live in `ddn-playwright-automation`.
- Standard workflow template: checkout, setup-node, cache npm, install deps,
  install browsers, run tests with `DASHBOARD_URL` & `DASHBOARD_API`, upload report.
- Do NOT recreate that YAML here; keep file count minimal.

Branch & Commit Guidance:
- Feature branches: `feature/<short-purpose>` (e.g., `feature/jenkins-init`).
- Commits: imperative mood, single focus area: `Add Jenkins start script`.
- Large doc updates: prefix with `docs:`; infra changes: `infra:`; scripts: `scripts:`.

AI Assistant Interaction Rules:
- When editing multiple files: batch related changes; keep patches minimal.
- Never reintroduce Playwright assets here unless explicitly requested.
- Before major doc restructures: summarize proposed new tree and wait for approval.
- Prefer providing run commands for any new executable script.

Sensitive Data & Secrets:
- Do not commit secrets, API keys, tokens or credentials.
- Use environment variables in workflows / local `.env` excluded by `.gitignore`.

Error Handling Expectations:
- Service start scripts must exit non-zero on failure and avoid silent retries.
- Recovery scripts should log actions with timestamps.

Performance Considerations:
- Avoid adding heavy dependencies to base image layers unless necessary.
- Defer optimization tasks until functional correctness and documentation tasks done.

Contact & Escalation:
- Architecture uncertainties → update `ARCHITECTURE-REALITY-CHECK.md` pending section.
- CI/test concerns → open issue in the Playwright repo, not here.

Revision History:
- 2025-11-26: Restored project instructions after accidental overwrite with Playwright workflow YAML.

Future Refinement Note:
After architecture diagrams (C4 levels, data flows) and the finalized service/port matrix are stable, schedule an instructions refresh. Goals for that pass:
- Integrate improved cross-repo testing guidance (backend vs Playwright automation coordination)
- Clarify parallel development workflows (feature branches + nightly UI tests + targeted backend checks)
- Add explicit AI assistant usage patterns for rapid test authoring and infra troubleshooting
- Include a concise decision tree: when to add tests, when to refactor, when to escalate
- Update CI examples (security scan workflow once added) without reintroducing UI test YAML here.

End of Instructions.
