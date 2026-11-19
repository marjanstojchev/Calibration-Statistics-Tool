# Robot Framework Testing Concept

## Purpose

Robot Framework covers the API and user-facing acceptance checks for the Calibration Statistics Tool. Pytest keeps unit and integration tests. Robot suites read like requirements, so they are the right place for API contracts and acceptance criteria.

## Test layers

| Layer | Target | Library | Where it runs |
|---|---|---|---|
| API (smoke now, contract later) | FastAPI `/api/*` on uvicorn :8000 | RequestsLibrary | `test:robot` job, no browser |
| Component (later) | One feature with fixture files, e.g. limits compute | RequestsLibrary | `test:robot` job |
| Acceptance | React app on :5173 | Browser (Playwright) | `test:robot-acceptance` job, after `build:frontend` |

## Folder layout

```
tests/robot/
  api/
    api_smoke.robot        # health, session summary, 400 on missing id, limits 422, session delete
  acceptance/
    homepage.robot         # title and main navigation tabs
```

`tests/tests_robot/` is the old sample project (login suite against `TestObject`). It is kept as an archived example and is not run by CI.

Add `resources/`, `component/`, and `fixtures/` folders when a suite needs shared keywords or sample files.

## Running locally

With the venv active:

```
robot --variable BASE_URL:http://localhost:8000 tests/robot/api
robot --variable FRONTEND_URL:http://localhost:5173 tests/robot/acceptance
```

Start the backend with `uvicorn api.main:app --port 8000`. Start the frontend with `npm run dev` in `cst-frontend`. For acceptance tests, run `rfbrowser init chromium` once.

Results go to `log.html`, `report.html`, and `output.xml` in the output directory.

## Pipeline

- `test:robot` (stage `test`): starts uvicorn, runs `tests/robot/api`, and publishes `xunit.xml` as a JUnit report.
- `test:robot-acceptance` (stage `test-e2e`): needs `build:frontend`, serves `cst-frontend/dist` on :5173 and starts uvicorn, then runs `tests/robot/acceptance`.
- Both jobs use `allow_failure: true` for now. Switch to blocking once the suites pass consistently.

## Linking tests to requirements (Jira)

Options, from least to most effort:

1. **Tags (start here):** tag each test with `REQ-<JIRA-KEY>` and put the Jira link in `Documentation`. Run one requirement with `robot --include REQ-123 tests/robot`. Robot's `output.xml` gives pass/fail per tag.
2. **Traceability table:** a small script reads `output.xml` and writes a markdown or HTML table of requirement → test → result for the CI artifacts.
3. **Jira import:** Xray or Zephyr can import Robot results and map them to Jira test cases. This needs the Jira plugin and an API token stored in CI variables.

Recommended path: option 1 now, option 2 when there are enough tagged tests, option 3 only if the team already uses Xray or Zephyr.

## Status

- Created: the API smoke suite, the homepage acceptance suite, the CI jobs, and the dev requirements.
- Validated: the `.robot` files parse, and the CI YAML parses.
- Not yet run: the suites haven't run against a live backend or frontend. Run them locally first, then check the first CI run.
- Pending: requirement tags and the traceability table, once Jira keys are available.
