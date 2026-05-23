from __future__ import annotations

from freshbench.schemas import (
    AssetState,
    AssetSubmission,
    RewardHint,
    ScoringReport,
    ValidationStageResult,
)
from freshbench.validator.model_panel import run_model_panel_calibration
from freshbench.validator.novelty import run_novelty_check
from freshbench.validator.scoring import run_ground_truth_check, run_schema_check


def validate_asset(submission: AssetSubmission) -> ScoringReport:
    stages: list[ValidationStageResult] = []

    schema_result = run_schema_check(submission)
    stages.append(schema_result)

    if not schema_result.passed:
        return _build_report(submission.task_id, stages, gate_failed=True)

    gt_result = run_ground_truth_check(submission)
    stages.append(gt_result)

    if not gt_result.passed:
        return _build_report(submission.task_id, stages, gate_failed=True)

    novelty_result = run_novelty_check(submission)
    stages.append(novelty_result)

    panel_result = run_model_panel_calibration(submission)
    stages.append(panel_result)

    return _build_report(submission.task_id, stages, gate_failed=False)


def _build_report(
    asset_id: str,
    stages: list[ValidationStageResult],
    *,
    gate_failed: bool,
) -> ScoringReport:
    if gate_failed:
        return ScoringReport(
            asset_id=asset_id,
            final_score=0.0,
            state=AssetState.REJECTED,
            stages=stages,
            reward_hint=RewardHint(submission_reward=0.0, usage_reward_weight=0.0),
        )

    final_score = _calculate_final_score(stages)
    state = _determine_state(final_score, stages)
    reward_hint = _calculate_reward(final_score, state)

    return ScoringReport(
        asset_id=asset_id,
        final_score=final_score,
        state=state,
        stages=stages,
        reward_hint=reward_hint,
    )


def _calculate_final_score(stages: list[ValidationStageResult]) -> float:
    score = 1.0
    for stage in stages:
        score *= stage.score
    return round(score, 4)


def _determine_state(final_score: float, stages: list[ValidationStageResult]) -> AssetState:
    if any(not s.passed for s in stages):
        return AssetState.REJECTED

    if final_score >= 0.5:
        return AssetState.ACTIVE
    if final_score >= 0.2:
        return AssetState.VERIFIED

    return AssetState.REJECTED


def _calculate_reward(final_score: float, state: AssetState) -> RewardHint:
    if state == AssetState.REJECTED:
        return RewardHint(submission_reward=0.0, usage_reward_weight=0.0)

    if state == AssetState.VERIFIED:
        return RewardHint(submission_reward=0.05, usage_reward_weight=final_score)

    return RewardHint(
        submission_reward=0.1,
        usage_reward_weight=round(final_score, 4),
    )
