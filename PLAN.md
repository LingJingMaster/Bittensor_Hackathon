# FreshBench Implementation Plan

## Collaboration Rule

Every AI or engineer must update this file immediately after completing a phase.

Required update after each phase:

- Change phase status.
- Add completed files/modules.
- Add validation command.
- Add validation result.
- Add blocker if any.
- Add next recommended step.

Do not mark a phase completed without validation evidence.

## Current Objective

Build a Railway-deployable FreshBench demo:

- FastAPI backend
- Static demo page
- JSON storage
- Modular validator pipeline
- Mock Bittensor weights
- No real chain integration in v1

## Phase Status

Status values: `pending`, `in_progress`, `completed`, `blocked`.

| Phase | Status | Owner | Validation | Notes |
| --- | --- | --- | --- | --- |
| Phase 0: Bootstrap | pending | Shared | - | Create Python project foundation with uv. |
| Phase 1: Schemas | pending | Shared | - | Define the core submission and report contracts. Freeze before parallel work. |
| Phase 2: Validator Pipeline | pending | Partner B: Validator/Demo | - | Implement modular scoring stages. |
| Phase 3: JSON Storage | pending | Partner A: Platform/API | - | Persist submissions and reports locally. |
| Phase 4: Demo Assets | pending | Partner B: Validator/Demo | - | Add good, bad, and near-duplicate sample assets. |
| Phase 5: FastAPI API | pending | Partner A: Platform/API | - | Expose health, validation, report, and sample endpoints. |
| Phase 6: Static Demo UI | pending | Partner B: Validator/Demo | - | Serve a simple demo page from FastAPI. |
| Phase 7: Railway Deployment | pending | Partner A: Platform/API | - | Deploy the public demo to Railway. |
| Phase 8: Upgrade Path | pending | Partner B: Validator/Demo | - | Document the path to frontend split, DB, model panel, and Bittensor SDK. |

## Two-Person Work Split

Phase 0 and Phase 1 are shared contract phases. Do not start independent implementation until both are completed and validated.

After Phase 1, split work into two isolated workstreams.

### Partner A: Platform/API Workstream

Primary ownership:

- Phase 3: JSON Storage
- Phase 5: FastAPI API
- Phase 7: Railway Deployment

Responsibilities:

- Keep API endpoints stable.
- Keep file storage behavior predictable.
- Keep FastAPI routes thin and delegate business logic to `freshbench/`.
- Keep Railway deployability intact.
- Provide fixture-backed API behavior if Partner B's validator pipeline is not ready yet.

Partner A must not redesign validator scoring or schema fields without coordinating in Phase 1 contract notes.

### Partner B: Validator/Demo Workstream

Primary ownership:

- Phase 2: Validator Pipeline
- Phase 4: Demo Assets
- Phase 6: Static Demo UI
- Phase 8: Upgrade Path

Responsibilities:

- Keep all scoring logic inside `freshbench/validator/`.
- Make good, bad, and near-duplicate behavior visibly different.
- Build UI against the stable API contract and sample report fixtures.
- Use mock/sample reports if Partner A's API is not ready yet.
- Document upgrade path without changing v1 API contract.

Partner B must not change API endpoint names, response shapes, or storage paths without coordinating in Phase 1 contract notes.

## Integration Rules

Use these contracts to prevent one workstream from blocking or breaking the other.

Shared contracts after Phase 1:

- `AssetSubmission` schema
- `ScoringReport` schema
- `ValidationStageResult` schema
- sample asset JSON shape
- sample report JSON shape
- API paths listed in the API Contract section

Parallel work rules:

- Partner A can build API and storage using fixture reports before the real validator is ready.
- Partner B can build validator and UI using local sample JSON before the API is ready.
- Each workstream must keep its own tests passing before integration.
- Integration happens only through the shared schemas and API contract.
- If a contract change is unavoidable, update `PLAN.md`, implementation guide, tests, and both partners' notes before coding against the new contract.

Merge order:

1. Complete Phase 0 and Phase 1 together.
2. Partner A starts Phase 3 while Partner B starts Phase 2.
3. Partner B adds Phase 4 sample assets once schemas are stable.
4. Partner A builds Phase 5 API against schemas and sample reports.
5. Partner B builds Phase 6 UI against API contract and sample data.
6. Partner A deploys Phase 7 after Phases 2-6 are validated locally.
7. Partner B completes Phase 8 upgrade documentation after deployment constraints are known.

Fallback rule:

- If Partner A is blocked, Partner B continues with local files and mock reports.
- If Partner B is blocked, Partner A continues with fixture reports and API/storage/deploy wiring.
- No phase may be marked completed solely because the other workstream is blocked.

## Phase Details

### Phase 0: Bootstrap

Goal: create Python project foundation with uv.

Expected files/modules:

- `pyproject.toml`
- package directories for `apps/`, `freshbench/`, `tests/`
- initial test placeholder

Validation:

- `uv sync`
- `uv run pytest`

### Phase 1: Schemas

Goal: define `AssetSubmission`, `GroundTruth`, `ValidationStageResult`, and `ScoringReport`.

Expected files/modules:

- `freshbench/schemas.py` or `freshbench/schemas/`
- schema unit tests under `tests/`

Validation:

- schema tests pass
- invalid submissions fail predictably
- JSON round-trip preserves required fields

### Phase 2: Validator Pipeline

Goal: implement modular validation stages.

Expected files/modules:

- `freshbench/validator/pipeline.py`
- `freshbench/validator/scoring.py`
- `freshbench/validator/novelty.py`
- `freshbench/validator/model_panel.py`

Validation:

- good asset becomes `active`
- bad asset becomes `rejected`
- near-duplicate receives low novelty score
- every stage returns score, pass/fail, reason, evidence, and timing

### Phase 3: JSON Storage

Goal: persist submissions and reports locally.

Expected files/modules:

- `freshbench/storage/json_store.py`
- `data/reports/`
- `data/submissions/`

Validation:

- save/load/list reports work
- empty store does not crash
- missing report returns a predictable not-found result

### Phase 4: Demo Assets

Goal: create good, bad, and near-duplicate sample assets.

Expected files/modules:

- `data/samples/good_document_asset.json`
- `data/samples/bad_ambiguous_asset.json`
- `data/samples/near_duplicate_asset.json`

Validation:

- all samples load
- all samples produce distinct reports
- good, bad, and near-duplicate behavior is visible in report output

### Phase 5: FastAPI API

Goal: expose health, validation, reports, and demo sample APIs.

Expected files/modules:

- `apps/api/main.py`
- API tests under `tests/`

Validation:

- `/health` returns ok
- `/docs` works locally
- `POST /api/assets/validate` returns `ScoringReport`
- report endpoints return saved reports

### Phase 6: Static Demo UI

Goal: serve a simple page from FastAPI.

Expected files/modules:

- `apps/api/static/index.html`
- `apps/api/static/app.js`
- `apps/api/static/styles.css`

Validation:

- user can select sample
- user can click validate
- page displays stages, final score, and lifecycle state
- UI calls relative API paths so Railway needs no frontend config

### Phase 7: Railway Deployment

Goal: deploy public demo to Railway.

Expected files/modules:

- `railway.json`
- README deployment notes updated if needed

Validation:

- `railway up`
- `railway logs`
- public `/health` works
- public demo page runs full validation

### Phase 8: Upgrade Path

Goal: document next path to Vite frontend, PostgreSQL, real model panel, and Bittensor SDK.

Expected files/modules:

- implementation guide updated with upgrade notes
- proposal or technical stack docs updated if needed

Validation:

- docs explain upgrade without changing API contract
- future frontend separation path is explicit
- production subnet boundaries are clear

## API Contract

The v1 API contract is fixed for the single-service demo and later frontend split.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Deployment and healthcheck endpoint. |
| `POST` | `/api/assets/validate` | Validate one `AssetSubmission` and return `ScoringReport`. |
| `GET` | `/api/reports` | List saved reports. |
| `GET` | `/api/reports/{asset_id}` | Load one saved report. |
| `GET` | `/api/demo/samples` | List available demo sample assets. |

## AI Collaboration Requirement

Every AI working on this repo must follow this protocol.

Before starting work:

- Read this file.
- Pick the first `pending` or `blocked` phase that can be advanced.
- Mark it `in_progress`.
- Keep ownership and notes current.

During work:

- Keep changes scoped to the active phase.
- Do not silently jump phases.
- Do not mark a phase completed without validation evidence.

After finishing a phase:

- Run the phase validation commands.
- Update this file immediately.
- Add an Update Log entry.
- Commit the change with a phase-specific commit message.

If blocked:

- Mark the phase `blocked`.
- Write the blocker.
- Write the exact next action needed.

## Update Log

Append one entry after each completed phase.

Template:

```md
### YYYY-MM-DD HH:mm - Phase X completed

- AI/Engineer:
- Files changed:
- Validation command:
- Validation result:
- Next step:
```
