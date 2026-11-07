"""Unit tests for Pydantic core models and configuration."""

import pytest
from core.models import ConfidenceInterval, TaskComplexity, TaskDefinition

def test_task_definition_validation(sample_task_def: TaskDefinition):
    """Verifies that TaskDefinition validates required fields properly."""
    assert sample_task_def.id == "task_test_mock"
    assert sample_task_def.complexity == TaskComplexity.INTERMEDIATE
    assert sample_task_def.timeout_seconds == 30.0

def test_wilson_score_interval_extremes():
    """Verifies Wilson Score Interval behaves correctly at zero and perfect bounds."""
    # Zero successes
    ci_zero = ConfidenceInterval.calculate_wilson_interval(0, 10)
    assert ci_zero.lower_bound == 0.0
    assert 0.0 < ci_zero.upper_bound < 0.35

    # Perfect successes
    ci_full = ConfidenceInterval.calculate_wilson_interval(10, 10)
    assert ci_full.lower_bound > 0.65
    assert ci_full.upper_bound == 1.0

def test_wilson_score_interval_symmetry():
    """Verifies symmetry of Wilson interval at 50% success rate."""
    ci_half = ConfidenceInterval.calculate_wilson_interval(50, 100)
    center = (ci_half.lower_bound + ci_half.upper_bound) / 2.0
    assert abs(center - 0.5) < 0.05
