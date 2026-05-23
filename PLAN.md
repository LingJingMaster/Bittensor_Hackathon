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
| Phase 0: Bootstrap | pending | - | - | Create Python project foundation with uv. |
| Phase 1: Schemas | pending | - | - | Define the core submission and report contracts. |
| Phase 2: Validator Pipeline | pending | - | - | Implement modular scoring stages. |
| Phase 3: JSON Storage | pending | - | - | Persist submissions and reports locally. |
| Phase 4: Demo Assets | pending | - | - | Add good, bad, and near-duplicate sample assets. |
| Phase 5: FastAPI API | pending | - | - | Expose health, validation, report, and sample endpoints. |
| Phase 6: Static Demo UI | pending | - | - | Serve a simple demo page from FastAPI. |
| Phase 7: Railway Deployment | pending | - | - | Deploy the public demo to Railway. |
| Phase 8: Upgrade Path | pending | - | - | Document the path to frontend split, DB, model panel, and Bittensor SDK. |

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

