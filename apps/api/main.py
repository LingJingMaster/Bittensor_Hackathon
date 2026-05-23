from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

from freshbench.schemas import AssetSubmission, ScoringReport
from freshbench.storage.json_store import JsonStore
from freshbench.validator.pipeline import validate_asset


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"

app = FastAPI(title="FreshBench API", version="0.1.0")


def _get_store(request: Request) -> JsonStore:
    store = getattr(request.app.state, "store", None)
    if store is None:
        store = JsonStore()
        request.app.state.store = store
    return store


def _load_sample(path: Path) -> AssetSubmission:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return AssetSubmission.model_validate(payload)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/assets/validate", response_model=ScoringReport)
def validate_submission(
    submission: AssetSubmission,
    request: Request,
) -> ScoringReport:
    store = _get_store(request)
    report = validate_asset(submission)

    store.save_submission(submission)
    store.save_report(report)

    return report


@app.get("/api/reports", response_model=list[ScoringReport])
def get_reports(request: Request) -> list[ScoringReport]:
    store = _get_store(request)
    return store.list_reports()


@app.get("/api/reports/{asset_id}", response_model=ScoringReport)
def get_report(asset_id: str, request: Request) -> ScoringReport:
    store = _get_store(request)
    report = store.load_report(asset_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report not found: {asset_id}")
    return report


@app.get("/api/demo/samples", response_model=list[AssetSubmission])
def get_demo_samples() -> list[AssetSubmission]:
    if not SAMPLES_DIR.exists():
        return []
    return [_load_sample(path) for path in sorted(SAMPLES_DIR.glob("*_asset.json"))]
