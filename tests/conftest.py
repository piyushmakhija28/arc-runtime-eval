"""Shared pytest test configuration and fixtures."""

import pytest
from core.models import TaskDefinition

@pytest.fixture
def sample_task_def() -> TaskDefinition:
    """Fixture providing a valid TaskDefinition."""
    return TaskDefinition(
        id="task_test_mock",
        title="Mock Invariant Test",
        domain="AI Hardware Runtimes",
        complexity="INTERMEDIATE",
        prompt="Write a function foo() that returns 42.",
        target_invariant="Returns integer 42."
    )
