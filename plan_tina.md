# Tina Personal Plan

This file is Tina's personal execution plan. The shared source of truth is still `PLAN.md`.

Important collaboration reminder:

> Do not optimize only for your own tasks. Every phase you complete must leave LingJing able to continue without guessing your intent. Keep storage paths, API behavior, sample assets, mock reports, and validation evidence clear enough for LingJing to consume directly.

## Role

Tina owns the platform layer, integration layer, sample data, and deployment path.

Primary phases:

- Phase 3: JSON Storage
- Phase 4: Demo Assets
- Phase 5: FastAPI API
- Phase 7: Railway Deployment

Shared phases:

- Phase 0: Bootstrap
- Phase 1: Schemas
- Phase 8: Upgrade Path

## Contract Dependencies

Do not start Phase 3, Phase 4, or Phase 5 until Phase 1 schemas are agreed and validated.

Shared contracts Tina must respect:

- `AssetSubmission`
- `GroundTruth`
- `ValidationStageResult`
- `RewardHint`
- `ScoringReport`
- `validate_asset(submission: AssetSubmission) -> ScoringReport`
- API paths in `PLAN.md`
- sample asset JSON shape
- sample report JSON shape

If any contract needs to change:

1. Update `PLAN.md`.
2. Update `docs/freshbench-implementation-guide.md`.
3. Notify LingJing before coding against the change.
4. Add or update tests proving the new contract.

## Phase 0: Bootstrap Shared Work

Goal: ensure both collaborators use the same Python project foundation.

Tina responsibilities:

- Confirm `uv` setup works locally.
- Confirm project package imports work.
- Confirm initial test suite runs.
- Avoid adding deployment-specific config before the app entrypoint exists.

Validation:

```bash
uv sync
uv run pytest
```

After completion:

- Update `PLAN.md` Phase 0 status and Update Log with LingJing.

## Phase 1: Schemas Shared Work

Goal: freeze the interface contract before parallel implementation.

Tina responsibilities:

- Ensure schema can be serialized to JSON cleanly.
- Ensure storage can save and load `AssetSubmission` and `ScoringReport`.
- Ensure FastAPI can use the schemas as request and response models.
- Confirm report fields are enough for API and UI.

Validation:

```bash
uv run pytest tests/test_schemas.py
```

After completion:

- Freeze schema names and field names.
- Confirm LingJing can implement validator pipeline without storage/API internals.

## Phase 3: JSON Storage

Goal: persist submissions and reports locally.

Owned module:

- `freshbench/storage/json_store.py`

Required functions:

```python
save_submission(submission: AssetSubmission) -> str
save_report(report: ScoringReport) -> str
load_report(asset_id: str) -> ScoringReport | None
list_reports() -> list[ScoringReport]
```

Recommended storage layout:

```text
data/submissions/{task_id}.json
data/reports/{asset_id}.json
```

Compatibility obligations to LingJing:

- Do not mutate validator report fields while saving/loading.
- Preserve stage order in saved reports.
- Return predictable values for missing reports.
- Keep paths configurable enough for tests to use temp directories.
- Provide saved fixture reports LingJing can use for UI work if API is not ready.

Validation:

```bash
uv run pytest tests/test_json_store.py
```

Minimum scenarios:

- Save report creates JSON file.
- Load report reconstructs `ScoringReport`.
- List reports returns saved reports.
- Empty store returns an empty list.
- Missing report returns `None`.

After completion:

- Update `PLAN.md` Phase 3.
- Add Update Log entry.
- Tell LingJing where fixture reports are stored.

## Phase 4: Demo Assets

Goal: create good, bad, and near-duplicate sample assets.

Owned files:

- `data/samples/good_document_asset.json`
- `data/samples/bad_ambiguous_asset.json`
- `data/samples/near_duplicate_asset.json`

Important dependency:

- Phase 4 depends on Phase 1 schemas, not Phase 2 validator pipeline.
- Tina can write samples while LingJing works on Phase 2.

Compatibility obligations to LingJing:

- Keep sample assets small and readable.
- Make each sample's intent obvious from the title and fields.
- Do not rely on hidden external files in v1.
- Include enough content for novelty and ground truth checks.
- If adding mock reports, ensure they match `ScoringReport`.

Validation:

```bash
uv run python -m json.tool data/samples/good_document_asset.json
uv run python -m json.tool data/samples/bad_ambiguous_asset.json
uv run python -m json.tool data/samples/near_duplicate_asset.json
```

After pipeline is available:

```bash
uv run pytest tests/test_validator_pipeline.py
```

After completion:

- Update `PLAN.md` Phase 4.
- Add Update Log entry.
- Tell LingJing which sample should be active, rejected, and low-novelty.

## Phase 5: FastAPI API

Goal: expose the demo through stable HTTP endpoints.

Owned module:

- `apps/api/main.py`

Required endpoints:

- `GET /health`
- `POST /api/assets/validate`
- `GET /api/reports`
- `GET /api/reports/{asset_id}`
- `GET /api/demo/samples`

Compatibility obligations to LingJing:

- API must call only `validate_asset(submission)`, not private validator internals.
- If LingJing's pipeline is not ready, use a clearly named mock validator function.
- Do not change endpoint paths without updating `PLAN.md`.
- Do not change `ScoringReport` response shape for UI convenience.
- Ensure API errors are structured and readable.

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

After completion:

- Update `PLAN.md` Phase 5.
- Add Update Log entry.
- Confirm LingJing can build the UI against the API.

## Phase 7: Railway Deployment

Goal: deploy the public demo to Railway.

Owned files:

- `railway.json`
- README deployment note if needed

Railway docs:

https://docs.railway.com/

Required behavior:

- App listens on `$PORT`.
- Healthcheck path is `/health`.
- Start command launches FastAPI.
- Public demo page can run validation.

Compatibility obligations to LingJing:

- Do not require local frontend build tooling.
- Do not require local model weights on Railway.
- Do not deploy before Phases 2-6 pass locally.
- Record the public Railway URL in `PLAN.md` or README.

Validation:

```bash
railway up
railway logs
curl https://<railway-domain>/health
```

Manual checks:

- Public `/health` returns ok.
- Public demo page loads.
- Public demo page validates all three samples.

After completion:

- Update `PLAN.md` Phase 7.
- Add Update Log entry.
- Share public URL with LingJing for pitch/demo verification.

## Phase 8: Upgrade Path Shared Work

Goal: document how the demo grows into a real subnet-oriented system.

Tina focus:

- Vite/React frontend split.
- PostgreSQL or pgvector migration.
- Railway service boundaries.
- Storage and API compatibility.
- Deployment cost and operational notes.

Validation:

- Docs explain upgrade without changing v1 API contract.
- LingJing can identify which parts remain validator work and which become platform work.

## Personal Guardrails

- Do not change schema fields casually.
- Do not make API response shapes convenient for storage but hard for UI.
- Do not let sample assets drift away from schema.
- Do not make deployment require unavailable local files.
- Do not mark a phase completed without validation output.
- Always leave enough notes for LingJing to continue if you are unavailable.

