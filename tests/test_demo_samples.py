import json
from pathlib import Path

import pytest

from freshbench.schemas import AssetState, AssetSubmission
from freshbench.validator.novelty import reset_history
from freshbench.validator.pipeline import validate_asset


SAMPLES_DIR = Path(__file__).resolve().parents[1] / "data" / "samples"


@pytest.fixture(autouse=True)
def _clean_history():
    reset_history()
    yield
    reset_history()


def _load_sample(filename: str) -> AssetSubmission:
    sample_path = SAMPLES_DIR / filename
    payload = json.loads(sample_path.read_text(encoding="utf-8"))
    return AssetSubmission.model_validate(payload)


def test_all_demo_sample_assets_load_as_submissions():
    expected_files = [
        "good_document_asset.json",
        "bad_ambiguous_asset.json",
        "near_duplicate_asset.json",
    ]

    for filename in expected_files:
        submission = _load_sample(filename)
        assert submission.task_id
        assert submission.skill_tags


def test_good_demo_sample_becomes_active():
    report = validate_asset(_load_sample("good_document_asset.json"))

    assert report.state == AssetState.ACTIVE
    assert report.final_score > 0.5
    assert [stage.stage for stage in report.stages] == [
        "schema_check",
        "ground_truth_check",
        "novelty_check",
        "model_panel_calibration",
    ]
    assert all(stage.passed for stage in report.stages)


def test_bad_demo_sample_is_rejected_at_schema_gate():
    report = validate_asset(_load_sample("bad_ambiguous_asset.json"))

    assert report.state == AssetState.REJECTED
    assert report.final_score == 0.0
    assert report.stages[0].stage == "schema_check"
    assert report.stages[0].passed is False


def test_near_duplicate_demo_sample_has_low_novelty_but_distinct_report():
    report = validate_asset(_load_sample("near_duplicate_asset.json"))
    novelty_stage = next(stage for stage in report.stages if stage.stage == "novelty_check")

    assert report.state == AssetState.VERIFIED
    assert 0.2 <= report.final_score < 0.5
    assert novelty_stage.passed is True
    assert novelty_stage.score < 0.7
    assert novelty_stage.evidence["max_benchmark_similarity"] >= 0.5


def test_demo_samples_produce_visible_behavior_differences():
    reports = {
        "good": validate_asset(_load_sample("good_document_asset.json")),
        "bad": validate_asset(_load_sample("bad_ambiguous_asset.json")),
        "near_duplicate": validate_asset(_load_sample("near_duplicate_asset.json")),
    }

    assert reports["good"].state == AssetState.ACTIVE
    assert reports["bad"].state == AssetState.REJECTED
    assert reports["near_duplicate"].state == AssetState.VERIFIED

    assert reports["good"].final_score > reports["near_duplicate"].final_score
    assert reports["near_duplicate"].final_score > reports["bad"].final_score
