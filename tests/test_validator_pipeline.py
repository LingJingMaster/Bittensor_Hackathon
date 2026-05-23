import pytest

from freshbench.schemas import (
    AssetState,
    AssetSubmission,
    GroundTruth,
    SourceType,
    TaskType,
    VerificationMethod,
)
from freshbench.validator.novelty import reset_history
from freshbench.validator.pipeline import validate_asset


@pytest.fixture(autouse=True)
def _clean_history():
    reset_history()
    yield
    reset_history()


def _good_submission() -> AssetSubmission:
    return AssetSubmission(
        task_id="freshbench_doc_good_001",
        task_type=TaskType.DOCUMENT_EXTRACTION,
        prompt="Extract the supplier name, invoice number, date, and total amount from this procurement invoice for a manufacturing parts order.",
        context="INVOICE #PO-2026-4471\nSupplier: Precision Parts GmbH\nDate: 2026-04-15\nItem: Titanium bolts x500 @ $2.30\nItem: Carbon washers x1000 @ $0.85\nSubtotal: $2,000.00\nTax (8%): $160.00\nTotal: $2,160.00",
        ground_truth=GroundTruth(
            expected_output={
                "supplier_name": "Precision Parts GmbH",
                "invoice_number": "PO-2026-4471",
                "date": "2026-04-15",
                "total": "2160.00",
            },
            verification_method=VerificationMethod.EXACT_MATCH,
        ),
        skill_tags=["multi_field_extraction", "schema_following", "numeric_parsing"],
        difficulty_estimate=0.45,
        source_type=SourceType.SYNTHETIC,
        anti_contamination_evidence="Generated from custom procurement template with randomized supplier names, part types, quantities, and pricing. Not derived from any public benchmark dataset.",
    )


def _bad_submission() -> AssetSubmission:
    return AssetSubmission(
        task_id="freshbench_doc_bad_001",
        task_type=TaskType.DOCUMENT_EXTRACTION,
        prompt="Extract data from this document.",
        context="Some text here.",
        ground_truth=GroundTruth(
            expected_output={},
            verification_method=VerificationMethod.EXACT_MATCH,
        ),
        skill_tags=["extraction"],
        difficulty_estimate=0.1,
        source_type=SourceType.SYNTHETIC,
        anti_contamination_evidence="Made up.",
    )


def _near_duplicate_submission() -> AssetSubmission:
    return AssetSubmission(
        task_id="freshbench_doc_dup_001",
        task_type=TaskType.DOCUMENT_EXTRACTION,
        prompt="Extract the total amount from the following invoice document",
        context="Invoice Total: $500.00",
        ground_truth=GroundTruth(
            expected_output={"total": "500.00"},
            verification_method=VerificationMethod.EXACT_MATCH,
        ),
        skill_tags=["extraction"],
        difficulty_estimate=0.2,
        source_type=SourceType.SYNTHETIC,
        anti_contamination_evidence="Slightly modified from common extraction task.",
    )


class TestGoodAsset:
    def test_becomes_active(self):
        report = validate_asset(_good_submission())
        assert report.state == AssetState.ACTIVE

    def test_positive_final_score(self):
        report = validate_asset(_good_submission())
        assert report.final_score > 0.0

    def test_all_stages_pass(self):
        report = validate_asset(_good_submission())
        assert all(s.passed for s in report.stages)

    def test_has_submission_reward(self):
        report = validate_asset(_good_submission())
        assert report.reward_hint.submission_reward > 0.0

    def test_has_usage_reward_weight(self):
        report = validate_asset(_good_submission())
        assert report.reward_hint.usage_reward_weight > 0.0


class TestBadAsset:
    def test_becomes_rejected(self):
        report = validate_asset(_bad_submission())
        assert report.state == AssetState.REJECTED

    def test_final_score_zero(self):
        report = validate_asset(_bad_submission())
        assert report.final_score == 0.0

    def test_zero_reward(self):
        report = validate_asset(_bad_submission())
        assert report.reward_hint.submission_reward == 0.0
        assert report.reward_hint.usage_reward_weight == 0.0

    def test_has_failure_reason(self):
        report = validate_asset(_bad_submission())
        failed_stages = [s for s in report.stages if not s.passed]
        assert len(failed_stages) >= 1
        assert all(s.reason for s in failed_stages)


class TestNearDuplicate:
    def test_low_novelty_score(self):
        report = validate_asset(_near_duplicate_submission())
        novelty_stages = [s for s in report.stages if s.stage == "novelty_check"]
        assert len(novelty_stages) == 1
        assert novelty_stages[0].score < 0.7

    def test_novelty_evidence_present(self):
        report = validate_asset(_near_duplicate_submission())
        novelty_stages = [s for s in report.stages if s.stage == "novelty_check"]
        evidence = novelty_stages[0].evidence
        assert "max_benchmark_similarity" in evidence
        assert "novelty_score" in evidence


class TestExactDuplicate:
    def test_second_identical_rejected(self):
        sub = _good_submission()
        validate_asset(sub)

        report2 = validate_asset(sub)
        novelty_stages = [s for s in report2.stages if s.stage == "novelty_check"]
        assert len(novelty_stages) == 1
        assert novelty_stages[0].score == 0.0
        assert not novelty_stages[0].passed


class TestStageStructure:
    def test_every_stage_has_required_fields(self):
        report = validate_asset(_good_submission())
        for stage in report.stages:
            assert stage.stage
            assert 0.0 <= stage.score <= 1.0
            assert isinstance(stage.passed, bool)
            assert stage.reason
            assert isinstance(stage.evidence, dict)
            assert stage.cost_ms >= 0.0

    def test_four_stages_for_good_asset(self):
        report = validate_asset(_good_submission())
        assert len(report.stages) == 4
        stage_names = [s.stage for s in report.stages]
        assert stage_names == [
            "schema_check",
            "ground_truth_check",
            "novelty_check",
            "model_panel_calibration",
        ]

    def test_early_exit_on_schema_failure(self):
        bad = _bad_submission()
        report = validate_asset(bad)
        assert len(report.stages) <= 2


class TestReportCompleteness:
    def test_report_always_has_asset_id(self):
        for sub in [_good_submission(), _bad_submission(), _near_duplicate_submission()]:
            report = validate_asset(sub)
            assert report.asset_id == sub.task_id

    def test_report_always_has_created_at(self):
        report = validate_asset(_good_submission())
        assert report.created_at is not None
