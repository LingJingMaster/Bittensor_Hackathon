from __future__ import annotations

import hashlib
import time
from difflib import SequenceMatcher
from typing import Any

from freshbench.schemas import AssetSubmission, ValidationStageResult

_KNOWN_BENCHMARKS: list[str] = [
    "Extract the total amount from the following invoice",
    "What is the vendor name in this document",
    "Parse the following receipt and return structured JSON",
    "Calculate the sum of all line items",
]

_submission_history: list[dict[str, str]] = []


def reset_history() -> None:
    _submission_history.clear()


def run_novelty_check(submission: AssetSubmission) -> ValidationStageResult:
    start = time.perf_counter()
    evidence: dict[str, Any] = {}

    prompt_hash = hashlib.sha256(submission.prompt.encode()).hexdigest()[:16]
    evidence["prompt_hash"] = prompt_hash

    exact_dup = _check_exact_duplicate(prompt_hash)
    evidence["exact_duplicate"] = exact_dup

    if exact_dup:
        elapsed = (time.perf_counter() - start) * 1000
        return ValidationStageResult(
            stage="novelty_check",
            score=0.0,
            passed=False,
            reason="Exact duplicate of a previous submission.",
            evidence=evidence,
            cost_ms=elapsed,
        )

    benchmark_sim = _check_benchmark_similarity(submission.prompt)
    evidence["max_benchmark_similarity"] = benchmark_sim

    history_sim = _check_history_similarity(submission.prompt)
    evidence["max_history_similarity"] = history_sim

    anti_contam_len = len(submission.anti_contamination_evidence.strip())
    evidence["anti_contamination_length"] = anti_contam_len

    novelty_score = _calculate_novelty_score(benchmark_sim, history_sim, anti_contam_len)
    evidence["novelty_score"] = novelty_score

    _submission_history.append({"hash": prompt_hash, "prompt": submission.prompt})

    passed = novelty_score >= 0.3
    elapsed = (time.perf_counter() - start) * 1000

    if not passed:
        reason = "Too similar to existing benchmarks or previous submissions."
    elif novelty_score >= 0.7:
        reason = "High novelty. No significant similarity to known benchmarks or history."
    else:
        reason = "Moderate novelty. Some similarity detected but within acceptable range."

    return ValidationStageResult(
        stage="novelty_check",
        score=round(novelty_score, 4),
        passed=passed,
        reason=reason,
        evidence=evidence,
        cost_ms=elapsed,
    )


def _check_exact_duplicate(prompt_hash: str) -> bool:
    return any(entry["hash"] == prompt_hash for entry in _submission_history)


def _check_benchmark_similarity(prompt: str) -> float:
    if not _KNOWN_BENCHMARKS:
        return 0.0
    prompt_lower = prompt.lower().strip()
    return max(
        SequenceMatcher(None, prompt_lower, bm.lower()).ratio()
        for bm in _KNOWN_BENCHMARKS
    )


def _check_history_similarity(prompt: str) -> float:
    if not _submission_history:
        return 0.0
    prompt_lower = prompt.lower().strip()
    return max(
        SequenceMatcher(None, prompt_lower, entry["prompt"].lower()).ratio()
        for entry in _submission_history
    )


def _calculate_novelty_score(
    benchmark_sim: float, history_sim: float, anti_contam_len: int
) -> float:
    max_sim = max(benchmark_sim, history_sim)

    if max_sim >= 0.9:
        base = 0.05
    elif max_sim >= 0.7:
        base = 0.3
    elif max_sim >= 0.5:
        base = 0.6
    else:
        base = 0.9

    contam_bonus = min(anti_contam_len / 200, 0.1)

    return min(base + contam_bonus, 1.0)
