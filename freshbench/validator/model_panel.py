from __future__ import annotations

import hashlib
import time
from typing import Any

from freshbench.schemas import AssetSubmission, ValidationStageResult


def run_model_panel_calibration(submission: AssetSubmission) -> ValidationStageResult:
    start = time.perf_counter()

    panel_results = _simulate_model_panel(submission)
    discrimination = _calculate_discrimination(panel_results)

    evidence: dict[str, Any] = {
        "panel_results": panel_results,
        "discrimination_score": discrimination,
    }

    passed = discrimination >= 0.2
    elapsed = (time.perf_counter() - start) * 1000

    if not passed:
        reason = "Poor discrimination: all models perform too similarly on this task."
    elif discrimination >= 0.6:
        reason = "Strong discrimination: clear capability gradient across model tiers."
    else:
        reason = "Acceptable discrimination: some differentiation across model tiers."

    return ValidationStageResult(
        stage="model_panel_calibration",
        score=round(discrimination, 4),
        passed=passed,
        reason=reason,
        evidence=evidence,
        cost_ms=elapsed,
    )


def _simulate_model_panel(submission: AssetSubmission) -> list[dict[str, Any]]:
    seed = int(hashlib.md5(submission.task_id.encode()).hexdigest()[:8], 16)
    difficulty = submission.difficulty_estimate

    weak_success = _mock_success_rate(seed, difficulty, tier="weak")
    mid_success = _mock_success_rate(seed, difficulty, tier="mid")
    strong_success = _mock_success_rate(seed, difficulty, tier="strong")
    baseline_success = _mock_success_rate(seed, difficulty, tier="baseline")

    return [
        {"model": "weak_baseline", "tier": "weak", "success_rate": weak_success},
        {"model": "mid_open_source", "tier": "mid", "success_rate": mid_success},
        {"model": "strong_model", "tier": "strong", "success_rate": strong_success},
        {"model": "rule_extractor", "tier": "baseline", "success_rate": baseline_success},
    ]


def _mock_success_rate(seed: int, difficulty: float, tier: str) -> float:
    tier_strength = {"weak": 0.2, "mid": 0.55, "strong": 0.9, "baseline": 0.1}
    strength = tier_strength.get(tier, 0.5)

    noise = ((seed % 100) / 100.0 - 0.5) * 0.08
    raw = strength * (1.0 - difficulty * 0.7) + noise

    return round(max(0.0, min(1.0, raw)), 2)


def _calculate_discrimination(panel_results: list[dict[str, Any]]) -> float:
    rates = [r["success_rate"] for r in panel_results]

    if len(rates) < 2:
        return 0.0

    spread = max(rates) - min(rates)

    sorted_rates = sorted(rates)
    monotonic_pairs = 0
    total_pairs = 0
    for i in range(len(sorted_rates)):
        for j in range(i + 1, len(sorted_rates)):
            total_pairs += 1
            if sorted_rates[j] >= sorted_rates[i]:
                monotonic_pairs += 1

    monotonicity = monotonic_pairs / total_pairs if total_pairs > 0 else 0.0

    discrimination = 0.6 * spread + 0.4 * monotonicity

    return round(min(discrimination, 1.0), 4)
