from pathlib import Path

import pytest

from freshbench import storage
from freshbench.schemas import (
    AssetState,
    AssetSubmission,
    GroundTruth,
    RewardHint,
    ScoringReport,
    SourceType,
    TaskType,
    ValidationStageResult,
    VerificationMethod,
)
from freshbench.storage.json_store import JsonStore


def _make_submission(task_id: str = "task_001") -> AssetSubmission:
    return AssetSubmission(
        task_id=task_id,
        task_type=TaskType.DOCUMENT_EXTRACTION,
        prompt="Extract vendor name and total.",
        context="Invoice #1001\nVendor: Acme Corp\nTotal: $1,234.56",
        ground_truth=GroundTruth(
            expected_output={"vendor_name": "Acme Corp", "total": "1234.56"},
            verification_method=VerificationMethod.EXACT_MATCH,
        ),
        skill_tags=["schema_following"],
        difficulty_estimate=0.5,
        source_type=SourceType.SYNTHETIC,
        anti_contamination_evidence="Generated from template.",
    )


def _make_stage(stage: str = "schema_check", score: float = 1.0, passed: bool = True):
    return ValidationStageResult(
        stage=stage,
        score=score,
        passed=passed,
        reason="ok",
        evidence={"k": 1},
        cost_ms=2.0,
    )


def _make_report(asset_id: str = "task_001") -> ScoringReport:
    return ScoringReport(
        asset_id=asset_id,
        final_score=0.8,
        state=AssetState.ACTIVE,
        stages=[_make_stage()],
        reward_hint=RewardHint(submission_reward=0.1, usage_reward_weight=0.8),
    )


@pytest.fixture
def store(tmp_path: Path) -> JsonStore:
    return JsonStore(base_dir=tmp_path)


class TestSaveSubmission:
    def test_save_submission_creates_file(self, store: JsonStore, tmp_path: Path):
        path_str = store.save_submission(_make_submission("task_a"))
        path = Path(path_str)
        assert path.exists()
        assert path.parent == tmp_path / "submissions"
        assert path.name == "task_a.json"

    def test_save_submission_is_valid_json(self, store: JsonStore):
        path_str = store.save_submission(_make_submission("task_b"))
        text = Path(path_str).read_text(encoding="utf-8")
        restored = AssetSubmission.model_validate_json(text)
        assert restored.task_id == "task_b"
        assert restored.ground_truth.verification_method == VerificationMethod.EXACT_MATCH


class TestSaveReport:
    def test_save_report_creates_file(self, store: JsonStore, tmp_path: Path):
        path_str = store.save_report(_make_report("task_b"))
        path = Path(path_str)
        assert path.exists()
        assert path.parent == tmp_path / "reports"
        assert path.name == "task_b.json"


class TestLoadReport:
    def test_load_report_reconstructs(self, store: JsonStore):
        original = _make_report("task_c")
        store.save_report(original)
        loaded = store.load_report("task_c")
        assert loaded is not None
        assert loaded.asset_id == original.asset_id
        assert loaded.final_score == original.final_score
        assert loaded.state == original.state
        assert len(loaded.stages) == len(original.stages)
        assert loaded.stages[0].stage == original.stages[0].stage
        assert loaded.reward_hint.submission_reward == original.reward_hint.submission_reward

    def test_load_missing_returns_none(self, store: JsonStore):
        assert store.load_report("does_not_exist") is None

    def test_load_missing_when_dir_absent(self, tmp_path: Path):
        store = JsonStore(base_dir=tmp_path / "fresh_unused")
        assert store.load_report("anything") is None


class TestListReports:
    def test_empty_store_returns_empty_list(self, store: JsonStore):
        assert store.list_reports() == []

    def test_empty_store_when_dir_absent(self, tmp_path: Path):
        store = JsonStore(base_dir=tmp_path / "never_created")
        assert store.list_reports() == []

    def test_list_returns_all_saved(self, store: JsonStore):
        store.save_report(_make_report("task_1"))
        store.save_report(_make_report("task_2"))
        store.save_report(_make_report("task_3"))
        reports = store.list_reports()
        assert len(reports) == 3
        asset_ids = {r.asset_id for r in reports}
        assert asset_ids == {"task_1", "task_2", "task_3"}


class TestStageOrderPreserved:
    def test_load_preserves_stage_order(self, store: JsonStore):
        original = ScoringReport(
            asset_id="task_ordered",
            final_score=0.7,
            state=AssetState.ACTIVE,
            stages=[
                _make_stage("schema_check", 1.0, True),
                _make_stage("ground_truth_check", 0.5, True),
                _make_stage("novelty_check", 0.0, False),
            ],
            reward_hint=RewardHint(submission_reward=0.1, usage_reward_weight=0.7),
        )
        store.save_report(original)
        loaded = store.load_report("task_ordered")
        assert loaded is not None
        assert [s.stage for s in loaded.stages] == [
            "schema_check",
            "ground_truth_check",
            "novelty_check",
        ]


class TestRoundTrip:
    def test_save_then_load_preserves_all_fields(self, store: JsonStore):
        original = _make_report("rt_task")
        store.save_report(original)
        loaded = store.load_report("rt_task")
        assert loaded is not None
        assert loaded.model_dump(mode="json") == original.model_dump(mode="json")


class TestModuleLevelHelpers:
    def test_module_exports_exist(self):
        from freshbench.storage import json_store

        assert callable(json_store.save_submission)
        assert callable(json_store.save_report)
        assert callable(json_store.load_report)
        assert callable(json_store.list_reports)
        assert hasattr(storage, "__name__")
