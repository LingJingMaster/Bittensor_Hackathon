from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from freshbench.schemas import AssetState
from freshbench.storage.json_store import JsonStore
from freshbench.validator.novelty import reset_history


SAMPLES_DIR = Path(__file__).resolve().parents[1] / "data" / "samples"


@pytest.fixture(autouse=True)
def _clean_app_state(tmp_path: Path):
    reset_history()
    app.state.store = JsonStore(base_dir=tmp_path)
    yield
    reset_history()
    if hasattr(app.state, "store"):
        delattr(app.state, "store")


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _sample_payload(filename: str) -> dict:
    return client_safe_json(SAMPLES_DIR / filename)


def client_safe_json(path: Path) -> dict:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def test_health_returns_ok(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_route_is_available(client: TestClient):
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_demo_samples_endpoint_lists_assets(client: TestClient):
    response = client.get("/api/demo/samples")

    assert response.status_code == 200
    payload = response.json()
    names = {sample["name"] for sample in payload}
    assert names == {"bad_ambiguous", "good_document", "near_duplicate"}
    for sample in payload:
        assert "label" in sample
        assert "submission" in sample
        assert sample["submission"]["task_id"]


def test_validate_asset_returns_report_and_saves_it(client: TestClient):
    submission = _sample_payload("good_document_asset.json")

    response = client.post("/api/assets/validate", json=submission)

    assert response.status_code == 200
    report = response.json()
    assert report["asset_id"] == submission["task_id"]
    assert report["state"] == AssetState.ACTIVE
    assert report["final_score"] > 0.5

    saved_response = client.get(f"/api/reports/{submission['task_id']}")
    assert saved_response.status_code == 200
    assert saved_response.json()["asset_id"] == submission["task_id"]


def test_reports_endpoint_lists_saved_reports(client: TestClient):
    good = _sample_payload("good_document_asset.json")
    bad = _sample_payload("bad_ambiguous_asset.json")
    client.post("/api/assets/validate", json=good)
    client.post("/api/assets/validate", json=bad)

    response = client.get("/api/reports")

    assert response.status_code == 200
    reports = response.json()
    assert {report["asset_id"] for report in reports} == {
        good["task_id"],
        bad["task_id"],
    }


def test_missing_report_returns_404(client: TestClient):
    response = client.get("/api/reports/missing_asset")

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found: missing_asset"


def test_invalid_submission_returns_422(client: TestClient):
    response = client.post("/api/assets/validate", json={"task_id": "missing_fields"})

    assert response.status_code == 422
