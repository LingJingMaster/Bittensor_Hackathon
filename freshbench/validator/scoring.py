from __future__ import annotations

import time
from typing import Any

from freshbench.schemas import (
    AssetSubmission,
    GroundTruth,
    TaskType,
    ValidationStageResult,
    VerificationMethod,
)


def run_schema_check(submission: AssetSubmission) -> ValidationStageResult:
    start = time.perf_counter()
    missing: list[str] = []

    if not submission.prompt.strip():
        missing.append("prompt is empty")
    if not submission.ground_truth.expected_output:
        missing.append("ground_truth.expected_output is empty")
    if not submission.anti_contamination_evidence.strip():
        missing.append("anti_contamination_evidence is empty")

    passed = len(missing) == 0
    elapsed = (time.perf_counter() - start) * 1000

    return ValidationStageResult(
        stage="schema_check",
        score=1.0 if passed else 0.0,
        passed=passed,
        reason="All required fields present and non-empty." if passed else f"Missing or empty: {', '.join(missing)}.",
        evidence={"missing_fields": missing, "fields_checked": 3},
        cost_ms=elapsed,
    )


def run_ground_truth_check(submission: AssetSubmission) -> ValidationStageResult:
    start = time.perf_counter()

    gt = submission.ground_truth
    task_type = submission.task_type

    issues: list[str] = []
    evidence: dict[str, Any] = {}

    if task_type == TaskType.DOCUMENT_EXTRACTION:
        score, field_evidence = _check_document_extraction_gt(gt)
        evidence.update(field_evidence)
    elif task_type == TaskType.MATH:
        score, field_evidence = _check_math_gt(gt)
        evidence.update(field_evidence)
    elif task_type == TaskType.CODING:
        score, field_evidence = _check_coding_gt(gt)
        evidence.update(field_evidence)
    else:
        score = _check_generic_gt(gt)

    if score == 0.0:
        issues.append("ground truth validation failed")

    passed = score > 0.0
    elapsed = (time.perf_counter() - start) * 1000

    return ValidationStageResult(
        stage="ground_truth_check",
        score=score,
        passed=passed,
        reason="Ground truth is valid and verifiable." if passed else f"Ground truth issues: {'; '.join(issues) or 'invalid or empty answer'}.",
        evidence=evidence,
        cost_ms=elapsed,
    )


def _check_document_extraction_gt(gt: GroundTruth) -> tuple[float, dict[str, Any]]:
    output = gt.expected_output
    evidence: dict[str, Any] = {}

    if not output:
        return 0.0, {"reason": "expected_output is empty"}

    field_count = len(output)
    evidence["field_count"] = field_count

    non_empty = sum(1 for v in output.values() if v is not None and str(v).strip())
    evidence["non_empty_fields"] = non_empty

    if field_count == 0:
        return 0.0, evidence

    completeness = non_empty / field_count
    evidence["completeness"] = completeness

    if gt.verification_method not in (VerificationMethod.EXACT_MATCH, VerificationMethod.F1):
        evidence["warning"] = f"Unusual verification method for document extraction: {gt.verification_method}"
        completeness *= 0.8

    return round(min(completeness, 1.0), 4), evidence


def _check_math_gt(gt: GroundTruth) -> tuple[float, dict[str, Any]]:
    output = gt.expected_output
    answer = output.get("answer")

    if answer is None or str(answer).strip() == "":
        return 0.0, {"reason": "No answer field in expected_output"}

    return 1.0, {"answer_present": True, "answer_type": type(answer).__name__}


def _check_coding_gt(gt: GroundTruth) -> tuple[float, dict[str, Any]]:
    output = gt.expected_output

    has_tests = "test_cases" in output or "expected_stdout" in output
    if not has_tests:
        return 0.0, {"reason": "Coding task requires test_cases or expected_stdout in expected_output"}

    return 1.0, {"has_test_cases": True}


def _check_generic_gt(gt: GroundTruth) -> float:
    if not gt.expected_output:
        return 0.0
    return 1.0
