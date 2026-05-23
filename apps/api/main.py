from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from freshbench.schemas import AssetSubmission, ScoringReport
from freshbench.storage.json_store import JsonStore
from freshbench.validator.novelty import reset_history
from freshbench.validator.pipeline import validate_asset


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
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
    reset_history()
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


@app.get("/api/demo/samples")
def get_demo_samples() -> list[dict]:
    if not SAMPLES_DIR.exists():
        return []
    label_map = {
        "good_document": "Good Asset",
        "bad_ambiguous": "Bad Asset",
        "near_duplicate": "Near Duplicate",
    }
    results = []
    for path in sorted(SAMPLES_DIR.glob("*_asset.json")):
        submission = _load_sample(path)
        name = path.stem.replace("_asset", "")
        label = label_map.get(name, name.replace("_", " ").title())
        results.append({
            "name": name,
            "label": label,
            "submission": json.loads(submission.model_dump_json()),
        })
    return results


@app.get("/api/demo/validate/{sample_name}")
def validate_demo_sample(sample_name: str, request: Request) -> ScoringReport:
    filename = f"{sample_name}_asset.json"
    path = SAMPLES_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Sample not found: {sample_name}")
    reset_history()
    submission = _load_sample(path)
    store = _get_store(request)
    report = validate_asset(submission)
    store.save_submission(submission)
    store.save_report(report)
    return report


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")
