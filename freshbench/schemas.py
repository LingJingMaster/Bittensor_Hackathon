from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    DOCUMENT_EXTRACTION = "document_extraction"
    CODING = "coding"
    MATH = "math"
    RAG = "rag"
    TOOL_USE = "tool_use"


class VerificationMethod(str, Enum):
    EXACT_MATCH = "exact_match"
    F1 = "f1"
    UNIT_TEST = "unit_test"
    SYMBOLIC_SOLVER = "symbolic_solver"
    CITATION_SPAN = "citation_span"
    SANDBOX_EXECUTION = "sandbox_execution"


class SourceType(str, Enum):
    SYNTHETIC = "synthetic"
    TRANSFORMED_REAL = "transformed_real_task"
    HUMAN_AUTHORED = "human_authored"


class AssetState(str, Enum):
    CANDIDATE = "candidate"
    VERIFIED = "verified"
    ACTIVE = "active"
    SATURATED = "saturated"
    RETIRED = "retired"
    REJECTED = "rejected"


class GroundTruth(BaseModel):
    expected_output: dict[str, Any] = Field(
        description="The correct answer in structured form. For document_extraction: field-value pairs.",
    )
    verification_method: VerificationMethod
    scoring_script: str | None = Field(
        default=None,
        description="Optional inline scoring logic or script reference.",
    )


class AssetSubmission(BaseModel):
    task_id: str = Field(description="Unique identifier for this benchmark asset.")
    task_type: TaskType
    prompt: str = Field(description="The task description or question posed to the model.")
    context: str | None = Field(
        default=None,
        description="Additional context: document text, code snippet, or reference material.",
    )
    ground_truth: GroundTruth
    skill_tags: list[str] = Field(
        min_length=1,
        description="Capability labels, e.g. ['schema_following', 'multi_field_extraction'].",
    )
    difficulty_estimate: float = Field(
        ge=0.0,
        le=1.0,
        description="Miner's self-assessed difficulty. 0=trivial, 1=extremely hard.",
    )
    source_type: SourceType
    anti_contamination_evidence: str = Field(
        description="Explanation of why this task is novel and not from existing benchmarks.",
    )


class ValidationStageResult(BaseModel):
    stage: str = Field(description="Stage name, e.g. 'schema_check', 'ground_truth_check'.")
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    reason: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    cost_ms: float = Field(ge=0.0, description="Wall-clock time for this stage in milliseconds.")


class RewardHint(BaseModel):
    submission_reward: float = Field(
        ge=0.0,
        le=1.0,
        description="Immediate small reward for passing basic validation.",
    )
    usage_reward_weight: float = Field(
        ge=0.0,
        le=1.0,
        description="Weight for delayed usage-based reward. Higher = more valuable asset.",
    )


class ScoringReport(BaseModel):
    asset_id: str = Field(description="Matches the submission task_id.")
    final_score: float = Field(ge=0.0, le=1.0)
    state: AssetState
    stages: list[ValidationStageResult]
    reward_hint: RewardHint
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
