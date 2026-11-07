"""Pydantic data models and mathematical confidence interval contracts."""

from enum import Enum
import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TaskComplexity(str, Enum):
    """Task complexity rating reflecting hardware invariant depth."""
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    HARDWARE_EXPERT = "HARDWARE_EXPERT"

class TaskDefinition(BaseModel):
    """Definition and metadata for a benchmark evaluation task."""
    id: str = Field(..., description="Unique alphanumeric identifier, e.g. task_01_sycl_usm_barrier")
    title: str = Field(..., description="Human-readable title of the task")
    domain: str = Field(default="Accelerated AI Hardware Runtimes")
    complexity: TaskComplexity
    prompt: str = Field(..., description="The exact system/user prompt fed to the model")
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    target_invariant: str = Field(..., description="Hardware or memory invariant under test")
    timeout_seconds: float = 30.0

class TrialResult(BaseModel):
    """Result of an individual evaluation trial."""
    task_id: str
    model_id: str
    trial_index: int
    raw_output: str
    parsed_solution: Optional[str] = None
    is_valid_format: bool
    passed_invariants: bool
    numerical_score: float = Field(..., ge=0.0, le=1.0)
    execution_latency_ms: float
    error_message: Optional[str] = None

class ConfidenceInterval(BaseModel):
    """Wilson Score binomial confidence interval parameters."""
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.95

    @classmethod
    def calculate_wilson_interval(
        cls, successes: int, total: int, z: float = 1.96
    ) -> "ConfidenceInterval":
        """Calculates the Wilson score interval for binomial proportions.

        Args:
            successes: Number of successful trials.
            total: Total number of trials.
            z: Standard normal distribution critical value (default 1.96 for 95% CI).

        Returns:
            ConfidenceInterval: Lower and upper bounds bounded to [0.0, 1.0].
        """
        if total <= 0:
            return cls(lower_bound=0.0, upper_bound=0.0)
        p_hat = successes / total
        denominator = 1.0 + (z**2) / total
        center = p_hat + (z**2) / (2.0 * total)
        spread = z * math.sqrt((p_hat * (1.0 - p_hat) / total) + ((z**2) / (4.0 * (total**2))))
        lower = max(0.0, (center - spread) / denominator)
        upper = min(1.0, (center + spread) / denominator)
        return cls(lower_bound=round(lower, 4), upper_bound=round(upper, 4))

class TaskSummaryMetrics(BaseModel):
    """Aggregated statistical metrics for a specific task and model."""
    task_id: str
    model_id: str
    trials_count: int
    pass_at_1: float
    pass_pow_k: float
    wilson_ci: ConfidenceInterval
    mean_latency_ms: float

class OverallModelBenchmark(BaseModel):
    """Cumulative benchmark summary across all tasks for a model."""
    model_id: str
    total_tasks: int
    total_trials: int
    overall_pass_rate: float
    consistency_pass_pow_k: float
    overall_wilson_ci: ConfidenceInterval
    approximate_cost_usd: float
    task_metrics: List[TaskSummaryMetrics]
