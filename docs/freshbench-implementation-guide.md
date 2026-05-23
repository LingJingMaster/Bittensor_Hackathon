# FreshBench Implementation Guide

整理时间：2026-05-23

这份文档是 FreshBench 单服务 Demo 的工程实施手册。`PLAN.md` 负责实时进度和协作状态，本文件负责说明每一步怎么实现、怎么验证、怎么部署。

核心原则：

- 先做可信 validator loop，再做复杂 UI 或链上集成。
- 每个模块完成后立即 validation。
- FastAPI route 保持薄层，核心逻辑放在 `freshbench/` 包内。
- 第一版使用 JSON 文件存储，后续可替换为 PostgreSQL。
- 第一版使用 mock Bittensor weights，不接真实链。
- 单服务 Demo 可平滑升级为前后端分离，API contract 不变。

## 1. Target Architecture

第一版采用 Railway-deployable single service：

```text
Browser
  |
  v
FastAPI service
  |-- static demo page
  |-- validation API
  |-- report API
  |
  v
freshbench package
  |-- schemas
  |-- validator pipeline
  |-- JSON storage
  |-- mock Bittensor weights
  |
  v
data/
  |-- samples
  |-- submissions
  |-- reports
```

Recommended project structure:

```text
apps/
  api/
    main.py
    static/
      index.html
      app.js
      styles.css

freshbench/
  __init__.py
  schemas.py
  validator/
    __init__.py
    pipeline.py
    scoring.py
    novelty.py
    model_panel.py
  storage/
    __init__.py
    json_store.py
  bittensor/
    __init__.py
    mock_weights.py

data/
  samples/
  submissions/
  reports/

tests/
  test_schemas.py
  test_validator_pipeline.py
  test_json_store.py
  test_api.py

pyproject.toml
railway.json
PLAN.md
```

Validation after creating folders:

```bash
find apps freshbench data tests -maxdepth 3 -type d
```

Expected result: all top-level module directories exist.

## 2. Phase 0: Bootstrap

Goal: create a Python project foundation using `uv`.

Recommended dependencies:

- `fastapi`
- `uvicorn`
- `pydantic`
- `pytest`
- `httpx`
- `rapidfuzz`

Implementation notes:

- Use Python 3.11+.
- Use `pyproject.toml` as the source of dependencies.
- Add an initial smoke test so `pytest` has something to run.

Validation:

```bash
uv sync
uv run python --version
uv run pytest
```

Completion criteria:

- Dependencies install successfully.
- Test suite runs.
- `PLAN.md` Phase 0 is updated with command output summary.

## 3. Phase 1: Core Schemas

Goal: define the stable data contract for the entire system.

Module:

```text
freshbench/schemas.py
```

Required models:

- `GroundTruth`
- `AssetSubmission`
- `ValidationStageResult`
- `RewardHint`
- `ScoringReport`

Recommended fields for `AssetSubmission`:

- `task_id`
- `task_type`
- `title`
- `prompt`
- `input_payload`
- `ground_truth`
- `verification_method`
- `skill_tags`
- `difficulty_estimate`
- `source_type`
- `anti_contamination_evidence`

Recommended fields for `ValidationStageResult`:

- `name`
- `score`
- `passed`
- `reason`
- `evidence`
- `cost_ms`

Recommended fields for `ScoringReport`:

- `asset_id`
- `final_score`
- `state`
- `stages`
- `reward_hint`
- `created_at`

Validation tests:

```bash
uv run pytest tests/test_schemas.py
```

Required scenarios:

- Valid submission passes.
- Missing `task_id` fails.
- Missing `ground_truth` fails.
- Invalid `difficulty_estimate` outside `[0, 1]` fails.
- Report JSON round-trip preserves stage data.

Completion criteria:

- All schema tests pass.
- Invalid inputs fail with predictable validation errors.
- `PLAN.md` Phase 1 is updated.

## 4. Phase 2: Validator Pipeline

Goal: implement modular validation stages and final scoring.

Main function:

```python
validate_asset(submission: AssetSubmission) -> ScoringReport
```

Required stage functions:

- `run_schema_check`
- `run_ground_truth_check`
- `run_novelty_check`
- `run_model_panel_calibration`
- `calculate_final_score`

Stage behavior:

- Every stage returns `ValidationStageResult`.
- Every result includes score, pass/fail, reason, evidence, and timing.
- Severe validity failure sets final score to `0`.
- Near-duplicate assets get low novelty score.
- Good assets should become `active`.
- Bad assets should become `rejected`.

Scoring rule:

```text
final_score =
  validity_score
  * novelty_score
  * discrimination_score
  * reproducibility_score
  * skill_relevance_score
  * challenge_survival_score
```

For v1, `usage_score` stays out of the main formula and appears only in production roadmap notes.

Validation tests:

```bash
uv run pytest tests/test_validator_pipeline.py
```

Required scenarios:

- Good document asset becomes `active`.
- Ambiguous or invalid ground truth becomes `rejected`.
- Near-duplicate receives lower novelty than good asset.
- Final score is product-based, not additive.

Completion criteria:

- Pipeline tests pass.
- Reports explain why each asset passed or failed.
- `PLAN.md` Phase 2 is updated.

## 5. Phase 3: JSON Storage

Goal: persist submissions and reports locally for demo and API retrieval.

Module:

```text
freshbench/storage/json_store.py
```

Required functions:

```python
save_submission(submission: AssetSubmission) -> None
save_report(report: ScoringReport) -> None
load_report(asset_id: str) -> ScoringReport | None
list_reports() -> list[ScoringReport]
```

Storage layout:

```text
data/submissions/{task_id}.json
data/reports/{asset_id}.json
```

Validation tests:

```bash
uv run pytest tests/test_json_store.py
```

Required scenarios:

- Saving report creates JSON file.
- Loading report reconstructs `ScoringReport`.
- Listing empty directory returns empty list.
- Missing report returns `None`.

Completion criteria:

- Storage tests pass.
- No hidden dependency on current working directory.
- `PLAN.md` Phase 3 is updated.

## 6. Phase 4: Demo Assets

Goal: prepare three demo assets that make FreshBench behavior obvious.

Files:

```text
data/samples/good_document_asset.json
data/samples/bad_ambiguous_asset.json
data/samples/near_duplicate_asset.json
```

Asset meanings:

- `good_document_asset.json`: clear task, complete ground truth, useful difficulty.
- `bad_ambiguous_asset.json`: ambiguous or invalid ground truth.
- `near_duplicate_asset.json`: too similar to a known or existing sample.

Validation:

```bash
uv run pytest tests/test_validator_pipeline.py
```

Manual validation:

```bash
uv run python -m json.tool data/samples/good_document_asset.json
uv run python -m json.tool data/samples/bad_ambiguous_asset.json
uv run python -m json.tool data/samples/near_duplicate_asset.json
```

Completion criteria:

- All sample JSON files are valid.
- All samples can be loaded as `AssetSubmission`.
- Each sample produces a visibly different report.
- `PLAN.md` Phase 4 is updated.

## 7. Phase 5: FastAPI API

Goal: expose the demo through stable HTTP endpoints.

Module:

```text
apps/api/main.py
```

Public API contract:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Healthcheck endpoint. |
| `POST` | `/api/assets/validate` | Validate one asset and return a report. |
| `GET` | `/api/reports` | List saved reports. |
| `GET` | `/api/reports/{asset_id}` | Load one report. |
| `GET` | `/api/demo/samples` | List demo sample assets. |

Validation:

```bash
uv run pytest tests/test_api.py
uv run uvicorn apps.api.main:app --reload
```

Manual checks:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/demo/samples
```

Completion criteria:

- `/health` returns `{"status":"ok"}`.
- `/docs` opens locally.
- `POST /api/assets/validate` returns a full `ScoringReport`.
- `PLAN.md` Phase 5 is updated.

## 8. Phase 6: Static Demo UI

Goal: serve a simple demo page from the FastAPI service.

Files:

```text
apps/api/static/index.html
apps/api/static/app.js
apps/api/static/styles.css
```

Required UI behavior:

- List demo samples.
- Select one sample.
- Run validation.
- Display pipeline stages.
- Display final score.
- Display lifecycle state.
- Display reward hint.

Important constraint:

- Use relative API paths such as `/api/demo/samples`.
- Do not hardcode localhost or Railway domain.

Validation:

```bash
uv run uvicorn apps.api.main:app --reload
```

Manual checks:

- Open `http://127.0.0.1:8000/`.
- Select the good asset and validate it.
- Select the bad asset and validate it.
- Select the near-duplicate asset and validate it.
- Confirm the three reports differ.

Completion criteria:

- Demo page works locally.
- No separate frontend build is required.
- `PLAN.md` Phase 6 is updated.

## 9. Phase 7: Railway Deployment

Goal: deploy a public demo to Railway.

Railway docs:

https://docs.railway.com/

Required config:

```text
railway.json
```

Required Railway behavior:

- App listens on `$PORT`.
- Healthcheck path is `/health`.
- Start command launches FastAPI.

Recommended `railway.json` start command:

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "deploy": {
    "startCommand": "uv run uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

Railway commands:

```bash
railway login
railway init
railway up
railway logs
```

Validation:

```bash
railway logs
curl https://<railway-domain>/health
```

Manual checks:

- Public `/health` returns ok.
- Public demo page loads.
- Public demo page runs validation for all three samples.

Completion criteria:

- Railway deployment succeeds.
- Public URL is recorded in README or `PLAN.md`.
- `PLAN.md` Phase 7 is updated.

## 10. Phase 8: Upgrade Path

Goal: document how the single-service demo grows into a real subnet-oriented system.

Upgrade sequence:

1. Split static UI into Vite/React while keeping API paths unchanged.
2. Replace JSON storage with PostgreSQL.
3. Add pgvector or Qdrant for novelty search.
4. Replace mock model panel with pluggable model runners.
5. Add challenge workflow and delayed reward accounting.
6. Replace mock Bittensor weights with Bittensor SDK integration.
7. Move validator workers to dedicated runtime if Railway becomes too constrained.

Validation:

- API contract remains unchanged.
- Core validator functions remain inside `freshbench/`.
- FastAPI routes stay thin.
- Docs explain which components remain on Railway and which move to validator infrastructure.

Completion criteria:

- Upgrade path is documented.
- `PLAN.md` Phase 8 is updated.

## 11. Validation-First Workflow

Every function or module must be validated before the phase is marked completed.

For each phase, update `PLAN.md` with:

- changed files/modules
- validation command
- validation result
- blocker if any
- next recommended step

Never write `completed` without evidence.

Recommended commit pattern:

```text
Phase 0: Bootstrap FreshBench app
Phase 1: Add core schemas
Phase 2: Add validator pipeline
Phase 3: Add JSON storage
Phase 4: Add demo assets
Phase 5: Add FastAPI API
Phase 6: Add static demo UI
Phase 7: Add Railway deployment config
Phase 8: Document upgrade path
```

## 12. Notes for Future Frontend Split

The single-service design is not a dead end.

To split frontend later:

- Keep `POST /api/assets/validate` unchanged.
- Keep report endpoints unchanged.
- Move `apps/api/static/` into a Vite app.
- Configure Vite to call the same relative API paths in production.
- Keep all validator logic inside `freshbench/`.

This keeps the first demo fast while preserving a clean path to a richer UI.

