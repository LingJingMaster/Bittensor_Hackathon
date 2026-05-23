import json
from datetime import datetime

import pytest
from pydantic import ValidationError

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


def _make_ground_truth(**overrides):
    defaults = {
        "expected_output": {"vendor_name": "Acme Corp", "total": "1234.56"},
        "verification_method": VerificationMethod.EXACT_MATCH,
    }
    return GroundTruth(**{**defaults, **overrides})


def _make_submission(**overrides):
    defaults = {
        "task_id": "freshbench_doc_001",
        "task_type": TaskType.DOCUMENT_EXTRACTION,
        "prompt": "Extract vendor name and total from this invoice.",
        "context": "Invoice #1001\nVendor: Acme Corp\nTotal: $1,234.56",
        "ground_truth": _make_ground_truth(),
        "skill_tags": ["schema_following", "multi_field_extraction"],
        "difficulty_estimate": 0.4,
        "source_type": SourceType.SYNTHETIC,
        "anti_contamination_evidence": "Generated from template with randomized values.",
    }
    return AssetSubmission(**{**defaults, **overrides})


def _make_stage_result(**overrides):
    defaults = {
        "stage": "schema_check",
        "score": 1.0,
        "passed": True,
        "reason": "All required fields present.",
        "evidence": {"fields_checked": 8},
        "cost_ms": 2.5,
    }
    return ValidationStageResult(**{**defaults, **overrides})


def _make_report(**overrides):
    defaults = {
        "asset_id": "freshbench_doc_001",
        "final_score": 0.73,
        "state": AssetState.ACTIVE,
        "stages": [_make_stage_result()],
        "reward_hint": RewardHint(submission_reward=0.1, usage_reward_weight=0.73),
    }
    return ScoringReport(**{**defaults, **overrides})


class TestAssetSubmission:
    def test_valid_submission(self):
        sub = _make_submission()
        assert sub.task_id == "freshbench_doc_001"
        assert sub.task_type == TaskType.DOCUMENT_EXTRACTION
        assert len(sub.skill_tags) == 2

    def test_missing_task_id_fails(self):
        with pytest.raises(ValidationError):
            _make_submission(task_id=None)

    def test_empty_skill_tags_fails(self):
        with pytest.raises(ValidationError):
            _make_submission(skill_tags=[])

    def test_difficulty_out_of_range_fails(self):
        with pytest.raises(ValidationError):
            _make_submission(difficulty_estimate=1.5)
        with pytest.raises(ValidationError):
            _make_submission(difficulty_estimate=-0.1)

    def test_invalid_task_type_fails(self):
        with pytest.raises(ValidationError):
            _make_submission(task_type="invalid_type")

    def test_context_optional(self):
        sub = _make_submission(context=None)
        assert sub.context is None


class TestValidationStageResult:
    def test_valid_stage(self):
        stage = _make_stage_result()
        assert stage.passed is True
        assert stage.score == 1.0

    def test_score_out_of_range_fails(self):
        with pytest.raises(ValidationError):
            _make_stage_result(score=1.5)

    def test_negative_cost_fails(self):
        with pytest.raises(ValidationError):
            _make_stage_result(cost_ms=-1.0)


class TestScoringReport:
    def test_valid_report(self):
        report = _make_report()
        assert report.final_score == 0.73
        assert report.state == AssetState.ACTIVE
        assert len(report.stages) == 1
        assert isinstance(report.created_at, datetime)

    def test_report_created_at_default_utc(self):
        report = _make_report()
        assert report.created_at.tzinfo is not None

    def test_final_score_out_of_range_fails(self):
        with pytest.raises(ValidationError):
            _make_report(final_score=2.0)


class TestJsonRoundTrip:
    def test_submission_roundtrip(self):
        original = _make_submission()
        json_str = original.model_dump_json()
        parsed = json.loads(json_str)
        restored = AssetSubmission.model_validate(parsed)
        assert restored.task_id == original.task_id
        assert restored.ground_truth.expected_output == original.ground_truth.expected_output
        assert restored.skill_tags == original.skill_tags

    def test_report_roundtrip(self):
        original = _make_report()
        json_str = original.model_dump_json()
        parsed = json.loads(json_str)
        restored = ScoringReport.model_validate(parsed)
        assert restored.asset_id == original.asset_id
        assert restored.final_score == original.final_score
        assert restored.state == original.state
        assert len(restored.stages) == len(original.stages)
        assert restored.reward_hint.submission_reward == original.reward_hint.submission_reward
