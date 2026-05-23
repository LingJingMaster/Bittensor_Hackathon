# LingJing Personal Plan

This file is LingJing's personal execution plan. The shared source of truth is still `PLAN.md`.

Important collaboration reminder:

> Do not optimize only for your own tasks. Every phase you complete must leave Tina able to continue without guessing your intent. Keep schemas, function signatures, sample reports, and validation evidence clear enough for Tina to consume directly.

## Role

LingJing owns the FreshBench mechanism layer and demo interpretation layer.

Primary phases:

- Phase 2: Validator Pipeline
- Phase 6: Static Demo UI

Shared phases:

- Phase 0: Bootstrap
- Phase 1: Schemas
- Phase 8: Upgrade Path

## Contract Dependencies

Do not start Phase 2 or Phase 6 until Phase 1 schemas are agreed and validated.

Shared contracts LingJing must respect:

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
3. Notify Tina before coding against the change.
4. Add or update tests proving the new contract.

## Phase 0: Bootstrap Shared Work

Goal: ensure both collaborators use the same Python project foundation.

LingJing responsibilities:

- Review `pyproject.toml`.
- Confirm `uv sync` works.
- Confirm `uv run pytest` works.
- Do not add validator-specific dependencies unless they are needed by Phase 0.

Validation:

```bash
uv sync
uv run pytest
```

After completion:

- Update `PLAN.md` Phase 0 status and Update Log with Tina.

## Phase 1: Schemas Shared Work

Goal: freeze the interface contract before parallel implementation.

LingJing responsibilities:

- Ensure schema supports validator evidence:
  - stage name
  - score
  - passed
  - reason
  - evidence
  - cost_ms
- Ensure `ScoringReport` has enough fields for UI display:
  - asset_id
  - final_score
  - state
  - stages
  - reward_hint
  - created_at
- Confirm invalid submissions fail predictably.

Validation:

```bash
uv run pytest tests/test_schemas.py
```

After completion:

- Freeze schema names and field names.
- Confirm Tina can build storage and API without needing validator internals.

## Phase 2: Validator Pipeline

Goal: implement FreshBench's core scoring mechanism.

Owned modules:

- `freshbench/validator/pipeline.py`
- `freshbench/validator/scoring.py`
- `freshbench/validator/novelty.py`
- `freshbench/validator/model_panel.py`

Required public function:

```python
validate_asset(submission: AssetSubmission) -> ScoringReport
```

Required internal stages:

- `run_schema_check`
- `run_ground_truth_check`
- `run_novelty_check`
- `run_model_panel_calibration`
- `calculate_final_score`

Compatibility obligations to Tina:

- Do not make Tina's API layer import private validator internals.
- Keep `validate_asset` deterministic for demo samples.
- Return a complete `ScoringReport` even when validation fails.
- Make errors explainable through stage results instead of raising unexpected exceptions.
- Provide at least one fixture report Tina can use if API work starts before the pipeline is complete.

Validation:

```bash
uv run pytest tests/test_validator_pipeline.py
```

Minimum scenarios:

- Good asset becomes `active`.
- Bad asset becomes `rejected`.
- Near-duplicate asset receives low novelty score.
- Validity failure sets final score to `0`.
- Every stage includes reason and evidence.

After completion:

- Update `PLAN.md` Phase 2.
- Add Update Log entry.
- Tell Tina the exact import path for `validate_asset`.

## Phase 6: Static Demo UI

Goal: build the explanatory demo layer that makes the validator pipeline visible.

Owned files:

- `apps/api/static/index.html`
- `apps/api/static/app.js`
- `apps/api/static/styles.css`

UI requirements:

- List sample assets.
- Let the user choose a sample.
- Call `POST /api/assets/validate`.
- Render each validation stage.
- Render final score.
- Render lifecycle state.
- Render reward hint.

Compatibility obligations to Tina:

- Use relative API paths only.
- Do not hardcode localhost or Railway URLs.
- Do not require separate frontend build tooling in v1.
- If Tina's API is incomplete, build against saved sample report JSON first.
- Keep UI tolerant of extra fields in `ScoringReport`.

Validation:

```bash
uv run uvicorn apps.api.main:app --reload
```

Manual checks:

- Open `http://127.0.0.1:8000/`.
- Validate good sample.
- Validate bad sample.
- Validate near-duplicate sample.
- Confirm the three reports are visually distinct.

After completion:

- Update `PLAN.md` Phase 6.
- Add Update Log entry.
- Confirm Tina can deploy the page on Railway without frontend-specific setup.

## Phase 8: Upgrade Path Shared Work

Goal: document how the demo grows into a real subnet-oriented system.

LingJing focus:

- Real model panel strategy.
- Challenge mechanism.
- Bittensor SDK integration boundaries.
- How validator workers should move beyond Railway when needed.

Validation:

- Docs explain upgrade without changing v1 API contract.
- Tina can identify which parts remain platform work and which become validator work.

## Personal Guardrails

- Do not change schema fields casually.
- Do not turn UI into a separate Vite app in v1.
- Do not make Railway deployment depend on local model execution.
- Do not hide failures; surface them as `ValidationStageResult`.
- Do not mark a phase completed without validation output.
- Always leave enough notes for Tina to continue if you are unavailable.

